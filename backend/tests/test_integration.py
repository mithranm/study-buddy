import pytest
from flask import json, jsonify
import io
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
import logging
import sys
import time

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

@pytest.fixture(scope="module")
def app():
    # Start patches for nltk.download only
    with patch('src.main.nltk.download', return_value=None):
        # Create a temporary directory for all tests
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Initialize temporary directories
            temp_chroma_db = os.path.join(temp_dir, 'chroma_db')
            temp_raw_documents = os.path.join(temp_dir, 'raw-documents')
            temp_uploads = os.path.join(temp_dir, 'uploads')

            # Create necessary directories with appropriate permissions
            for dir_path in [temp_chroma_db, temp_raw_documents, temp_uploads]:
                os.makedirs(dir_path, exist_ok=True)
                os.chmod(dir_path, 0o777)  # Ensure read/write permissions
                logger.info(f"Created directory with permissions: {dir_path}")

            # Define test configuration
            test_config = {
                'TESTING': True,
                'CHROMA_DB_PATH': temp_chroma_db,
                'RAW_DOCUMENTS_PATH': temp_raw_documents,
                'UPLOAD_FOLDER': temp_uploads
            }
            
            logger.info("Creating app with test configuration")
            app = create_app(test_config)
            
            # Log the app configuration for verification
            logger.info("App configuration:")
            for key, value in app.config.items():
                logger.info(f"{key}: {value}")
            
            yield app

            # Teardown
            logger.info(f"Cleaning up temporary directory: {temp_dir}")

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def essay_content():
    return """
    The Importance of Sustainable Development

    Sustainable development has become a crucial concept in the 21st century as we face unprecedented environmental challenges. It refers to development that meets the needs of the present without compromising the ability of future generations to meet their own needs. This essay will explore the importance of sustainable development and its impact on our world.

    First and foremost, sustainable development is essential for environmental preservation. Our planet's resources are finite, and unsustainable practices have led to issues such as deforestation, pollution, and climate change. By adopting sustainable practices, we can reduce our environmental footprint and protect ecosystems for future generations.

    Secondly, sustainable development is crucial for economic stability. While traditional economic models often prioritize short-term gains, sustainable development focuses on long-term economic health. This approach can lead to the creation of new industries, such as renewable energy, and can help ensure the longevity of existing industries by promoting responsible resource management.

    Lastly, sustainable development is vital for social equity. It aims to improve the quality of life for all people, including those in developing countries and marginalized communities. By promoting access to education, healthcare, and clean resources, sustainable development can help reduce poverty and inequality on a global scale.

    In conclusion, sustainable development is not just an environmental issue, but a comprehensive approach to creating a better world. It balances economic growth, environmental protection, and social progress. As we move forward, it is crucial that governments, businesses, and individuals embrace sustainable practices to ensure a prosperous and healthy future for all.
    """

def test_entire_system(client, app, pytestconfig, essay_content):
    with app.app_context():
        # Reset ChromaDB client and embedding function to ensure test isolation
        vector_db.chroma_client = None
        vector_db.embedding_function = None

        # Initialize the ChromaDB collection
        get_collection()

        # Log the current configuration
        logger.info("Current app configuration:")
        for key, value in app.config.items():
            logger.info(f"{key}: {value}")

        # Step 1: Upload Document
        test_file = 'integration_test_essay.txt'
        
        upload_response = client.post('/api/upload', 
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(essay_content.encode('utf-8')), test_file)}
        )
        assert upload_response.status_code == 200
        assert 'File uploaded and embedded successfully' in upload_response.get_data(as_text=True)

        # Log the upload response
        logger.info(f"Upload response: {upload_response.get_data(as_text=True)}")

        # TESTING PDF HERE
        #Basically we needed pytest to pass what the root dir is, and then we can access test_upload
        test_pdf_path = os.path.join(pytestconfig.rootdir, 'test_upload', 'test.pdf')
        
        with open(test_pdf_path, "rb") as pdf:
            pdf_content = pdf.read()

        upload_response = client.post('/api/upload', 
            content_type='multipart/form-data',
            data={'file': (io.BytesIO(pdf_content), "test.pdf")}
        )

        assert upload_response.status_code == 200
        assert 'File uploaded and embedded successfully' in upload_response.get_data(as_text=True)

        # Log the PDF upload response
        logger.info(f"PDF upload response: {upload_response.get_data(as_text=True)}")
        
        # Optionally, verify that vectors are stored
        collection = get_collection()
        count = collection.count()
        logger.info(f"Number of vectors in collection after upload: {count}")
        assert count > 0, "ChromaDB should have at least one vector after embedding."
        
        search_response = client.post('/api/search', json={'query': 'sustainable development'})
        logger.info(search_response.get_json())
        assert search_response.status_code == 200
        assert 'documents' in search_response.get_json()
        
        # Step 2: Initiate Chat
        prompt = 'What do the sources say about sustainable development and climate change?'
        chat_response = client.post('/api/chat', json={'prompt': prompt, 'model': "llama3.2:3b"})
        logger.info(chat_response.get_json())
        assert chat_response.status_code == 200
        response_data = chat_response.get_json()
        assert 'message' in response_data
        logger.info(f"Chat Response: {response_data['message']}")