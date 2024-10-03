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

# Import get_collection if needed
from src.vector_db import get_collection

# Set up logging
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    
    # Create file handler and set level to debug
    log_file = 'test_integration.log'
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

class IntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start patches for nltk.download only
        cls.patcher_nltk = patch('src.main.nltk.download', return_value=None)
        cls.mock_nltk_download = cls.patcher_nltk.start()
        
        # Removed the patch for vector_db.get_collection
        # cls.patcher_vector_db = patch('src.main.vector_db.get_collection', return_value=MagicMock())
        # cls.mock_vector_db_get_collection = cls.patcher_vector_db.start()
        
        # Create a temporary directory for all tests
        cls.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {cls.temp_dir}")

    @classmethod
    def tearDownClass(cls):
        # Stop all patches
        cls.patcher_nltk.stop()
        # cls.patcher_vector_db.stop()  # Already removed
        
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

        # Initialize the ChromaDB collection with the temporary path
        get_collection()

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
    
    def test_entire_system(self):
        # Step 1: Upload Document
        test_file = 'integration_test_essay.txt'
        
        upload_response = self.client.post('/upload', 
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(self.essay_content.encode('utf-8')), test_file)}
        )
        self.assertEqual(upload_response.status_code, 200)
        self.assertIn('File uploaded and embedded successfully', upload_response.get_data(as_text=True))

        # TESTING PDF HERE ------------------------------------- NEWLY ADDED

        pdf = open("/test_upload/test.pdf", "rb")
        pdf_content = pdf.read()

        upload_response = self.client.post('/upload', 
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(pdf_content.encode('utf-8')), "test.pdf")}
        )

        self.assertEqual(upload_response.status_code, 200)
        self.assertIn('File uploaded and embedded successfully', upload_response.get_data(as_test=True))

        # END OF TESTING PDF ------------------------------------
        
        # Optionally, verify that vectors are stored
        collection = get_collection()
        count = collection.count()
        logger.info(f"Number of vectors in collection after upload: {count}")
        self.assertGreater(count, 0, "ChromaDB should have at least one vector after embedding.")
        
        search_response = self.client.post('/search', json={'query': 'sustainable development'})
        logger.info(search_response)
        self.assertEqual(search_response.status_code, 200)
        self.assertIn('documents', search_response.get_json())
        
        # Step 2: Initiate Chat
        prompt = 'What do the sources say about sustainable development?'
        chat_response = self.client.post('/chat', json={'prompt': prompt})
        self.assertEqual(chat_response.status_code, 200)
        response_data = chat_response.get_json()
        self.assertIn('message', response_data)
        logger.info(f"Chat Response: {response_data['message']}")

if __name__ == '__main__':
    unittest.main()
