import unittest
from flask import json
import io
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import logging

# Import the app factory function
from src.main import create_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {cls.temp_dir}")

    @classmethod
    def tearDownClass(cls):
        logger.info(f"Removing temporary directory: {cls.temp_dir}")
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        self.temp_chroma_db = os.path.join(self.temp_dir, 'chroma_db')
        self.temp_raw_documents = os.path.join(self.temp_dir, 'raw-documents')
        self.temp_uploads = os.path.join(self.temp_dir, 'uploads')

        for dir_path in [self.temp_chroma_db, self.temp_raw_documents, self.temp_uploads]:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

        self.test_config = {
            'TESTING': True,
            'CHROMA_DB_PATH': self.temp_chroma_db,
            'RAW_DOCUMENTS_PATH': self.temp_raw_documents,
            'UPLOAD_FOLDER': self.temp_uploads
        }
        
        logger.info("Creating app with test configuration")
        self.app = create_app(self.test_config)
        self.client = self.app.test_client()

        # Log all app configurations
        for key, value in self.app.config.items():
            logger.debug(f"App config: {key} = {value}")

        self.app.nltk_ready = True
        self.app.chroma_ready = True

    def tearDown(self):
        logger.info("Tearing down test case")
        for dir_path in [self.temp_chroma_db, self.temp_raw_documents, self.temp_uploads]:
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    logger.info(f"Removed: {file_path}")
                except Exception as e:
                    logger.error(f'Failed to delete {file_path}. Reason: {e}')

    @patch('src.main.ollama')
    @patch('src.main.nltk')
    @patch('src.main.vector_db')
    def test_status_endpoint(self, mock_vector_db, mock_nltk, mock_ollama):
        logger.info("Testing status endpoint")
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('nltk_ready', data)
        self.assertIn('chroma_ready', data)
        self.assertTrue(data['nltk_ready'])
        self.assertTrue(data['chroma_ready'])

    @patch('src.main.vector_db')
    @patch('src.main.chunker')
    def test_upload_file_success(self, mock_chunker, mock_vector_db):
        logger.info("Testing successful file upload")
        mock_vector_db.get_collection.return_value = MagicMock()
        test_file_content = b'Test content'
        test_file = 'test_file.txt'
        
        response = self.client.post('/upload', 
                                    content_type='multipart/form-data',
                                    data={'file': (io.BytesIO(test_file_content), test_file)})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'File uploaded and embedded successfully')
        
        expected_file_path = os.path.join(self.temp_uploads, test_file)
        self.assertTrue(os.path.exists(expected_file_path))
        mock_chunker.embed_documents.assert_called_once()

    def test_upload_file_no_file(self):
        logger.info("Testing file upload with no file")
        response = self.client.post('/upload', 
                                    content_type='multipart/form-data',
                                    data={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No file part')

    def test_upload_file_empty_filename(self):
        logger.info("Testing file upload with empty filename")
        response = self.client.post('/upload', 
                                    content_type='multipart/form-data',
                                    data={'file': (io.BytesIO(b''), '')})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No selected file')

    @patch('src.main.vector_db')
    def test_search_documents_success(self, mock_vector_db):
        logger.info("Testing successful document search")
        mock_vector_db.search_documents.return_value = json.dumps({'results': ['test result']}), 200
        
        response = self.client.post('/search', json={'query': 'test query'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertEqual(data['results'], ['test result'])

    def test_search_documents_no_query(self):
        logger.info("Testing document search with no query")
        response = self.client.post('/search', json={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_list_documents_success(self):
        logger.info("Testing successful document listing")
        test_files = ['file1.txt', 'file2.pdf', 'file3.docx']
        for file in test_files:
            with open(os.path.join(self.temp_uploads, file), 'w') as f:
                f.write('Test content')

        response = self.client.get('/documents')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        for file in test_files:
            self.assertIn(file, data)

    @patch('src.main.vector_db')
    def test_delete_document_success(self, mock_vector_db):
        logger.info("Testing successful document deletion")
        mock_vector_db.get_collection.return_value = MagicMock()
        test_file = 'test_delete.txt'
        with open(os.path.join(self.temp_uploads, test_file), 'w') as f:
            f.write('Test content for deletion')
        
        response = self.client.delete(f'/documents/{test_file}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Document deleted successfully')
        self.assertFalse(os.path.exists(os.path.join(self.temp_uploads, test_file)))
        mock_vector_db.get_collection().delete.assert_called_once()

    def test_delete_nonexistent_document(self):
        logger.info("Testing deletion of non-existent document")
        response = self.client.delete('/documents/nonexistent.txt')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Document not found')

    @patch('src.main.vector_db')
    def test_generate_success(self, mock_vector_db):
        logger.info("Testing successful generation")
        mock_vector_db.generate.return_value = json.dumps({'response': 'Generated content'}), 200
        
        response = self.client.post('/generate', json={'prompt': 'Test prompt'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertEqual(data['response'], 'Generated content')

    def test_generate_no_prompt(self):
        logger.info("Testing generation with no prompt")
        response = self.client.post('/generate', json={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()