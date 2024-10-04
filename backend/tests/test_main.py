import unittest
from flask import json, jsonify
import io
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import logging
import sys
import time  # Ensure time is imported

# Import the app factory function
from src.main import create_app

# Import vector_db to reset globals if needed
from src import vector_db

# Set up logging
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    
    # Create file handler and set level to debug
    log_file = 'test_main.log'
    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    
    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
    
    return logger

logger = setup_logging()

class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start patches for nltk.download and vector_db.get_collection
        cls.patcher_nltk = patch('src.main.nltk.download', return_value=None)
        cls.patcher_vector_db = patch('src.main.vector_db.get_collection', return_value=MagicMock())
        cls.mock_nltk_download = cls.patcher_nltk.start()
        cls.mock_vector_db_get_collection = cls.patcher_vector_db.start()
        
        # Create a temporary directory for all tests
        cls.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {cls.temp_dir}")

    @classmethod
    def tearDownClass(cls):
        # Stop all patches
        cls.patcher_nltk.stop()
        cls.patcher_vector_db.stop()
        
        # Remove temporary directory
        logger.info(f"Removing temporary directory: {cls.temp_dir}")
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        # Initialize temporary directories
        self.temp_chroma_db = os.path.join(self.temp_dir, 'chroma_db')
        self.temp_raw_documents = os.path.join(self.temp_dir, 'raw-documents')
        self.temp_uploads = os.path.join(self.temp_dir, 'uploads')

        # Create necessary directories with appropriate permissions
        for dir_path in [self.temp_chroma_db, self.temp_raw_documents, self.temp_uploads]:
            os.makedirs(dir_path, exist_ok=True)
            os.chmod(dir_path, 0o777)  # Ensure read/write permissions
            logger.info(f"Created directory with permissions: {dir_path}")

        # Define test configuration
        self.test_config = {
            'TESTING': True,
            'CHROMA_DB_PATH': self.temp_chroma_db,
            'RAW_DOCUMENTS_PATH': self.temp_raw_documents,
            'UPLOAD_FOLDER': self.temp_uploads
        }
        
        logger.info("Creating app with test configuration")
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Reset ChromaDB client and embedding function to ensure test isolation
        vector_db.chroma_client = None
        vector_db.embedding_function = None

        # Predefined essay content
        self.essay_content = """
        The Importance of Sustainable Development

        Sustainable development has become a crucial concept in the 21st century as we face unprecedented environmental challenges. It refers to development that meets the needs of the present without compromising the ability of future generations to meet their own needs. This essay will explore the importance of sustainable development and its impact on our world.

        First and foremost, sustainable development is essential for environmental preservation. Our planet's resources are finite, and unsustainable practices have led to issues such as deforestation, pollution, and climate change. By adopting sustainable practices, we can reduce our environmental footprint and protect ecosystems for future generations.

        Secondly, sustainable development is crucial for economic stability. While traditional economic models often prioritize short-term gains, sustainable development focuses on long-term economic health. This approach can lead to the creation of new industries, such as renewable energy, and can help ensure the longevity of existing industries by promoting responsible resource management.

        Lastly, sustainable development is vital for social equity. It aims to improve the quality of life for all people, including those in developing countries and marginalized communities. By promoting access to education, healthcare, and clean resources, sustainable development can help reduce poverty and inequality on a global scale.

        In conclusion, sustainable development is not just an environmental issue, but a comprehensive approach to creating a better world. It balances economic growth, environmental protection, and social progress. As we move forward, it is crucial that governments, businesses, and individuals embrace sustainable practices to ensure a prosperous and healthy future for all.
        """

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
        # No need to remove temp_dir here as it's handled in tearDownClass
        logger.info(f"Test case teardown complete.")

    @patch('src.main.vector_db')
    def test_status_endpoint(self, mock_vector_db):
        logger.info("Testing status endpoint")
        # Mock the vector_db.get_collection to prevent actual DB operations
        mock_vector_db.get_collection.return_value = MagicMock()
        response = self.client.get('/api/status')
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
        test_file = 'test_essay.txt'
        
        response = self.client.post('/api/upload', 
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(self.essay_content.encode('utf-8')), test_file)})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'File uploaded and embedded successfully')

        expected_file_path = os.path.join(self.temp_uploads, test_file)
        self.assertTrue(os.path.exists(expected_file_path))
        mock_chunker.embed_documents.assert_called_once()

    def test_upload_file_no_file(self):
        logger.info("Testing file upload with no file")
        response = self.client.post('/api/upload', 
                                    content_type='multipart/form-data',
                                    data={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No file part')

    def test_upload_file_empty_filename(self):
        logger.info("Testing file upload with empty filename")
        response = self.client.post('/api/upload', 
                                    content_type='multipart/form-data',
                                    data={'file': (io.BytesIO(b''), '')})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No selected file')

    @patch('src.main.vector_db')
    def test_search_documents_success(self, mock_vector_db):
        logger.info("Testing successful document search")
        mock_vector_db.search_documents.return_value = {'documents': [['test result']]}, 200
        
        response = self.client.post('/api/search', json={'query': 'test query'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['documents'], [['test result']])

    def test_search_documents_no_query(self):
        logger.info("Testing document search with no query")
        response = self.client.post('/api/search', json={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No query provided')

    def test_list_documents_success(self):
        logger.info("Testing successful document listing")
        test_files = ['file1.txt', 'file2.pdf', 'file3.docx']
        for file in test_files:
            with open(os.path.join(self.temp_uploads, file), 'w') as f:
                f.write('Test content')

        response = self.client.get('/api/documents')
        
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
        
        response = self.client.delete(f'/api/documents/{test_file}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Document deleted successfully')
        self.assertFalse(os.path.exists(os.path.join(self.temp_uploads, test_file)))
        mock_vector_db.get_collection().delete.assert_called_once()

    def test_delete_nonexistent_document(self):
        logger.info("Testing deletion of non-existent document")
        response = self.client.delete('/api/documents/nonexistent.txt')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Document not found')

    @patch('src.main.vector_db.search_documents')
    @patch('src.ollama_calls.chat')
    def test_chat_success(self, mock_chat, mock_search):
        logger.info("Testing successful chat")
        mock_search.return_value = {'documents': [['test result 1', 'test result 2']]}, 200
        mock_chat.return_value = jsonify({'message': 'Ollama response'}), 200

        response = self.client.post('/api/chat', json={'prompt': 'What do the sources say?'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        logger.info('Response From Ollama: %s', data['message'])
        self.assertEqual(data['message'], 'Ollama response')

    def test_chat_no_prompt(self):
        logger.info("Testing generation with no prompt")
        response = self.client.post('/api/chat', json={})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
