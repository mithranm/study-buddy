import chromadb
from flask import request, jsonify, current_app
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
from chromadb.config import Settings
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables to store the Embedding Function and Chroma Client so they don't get made more than once
chroma_client = None
embedding_function = None

# HELPER METHODS

def get_chroma_client(max_retries=5, retry_delay=5):
    global chroma_client
    retries = 0
    while retries < max_retries:
        try:
            if chroma_client is None:
                chroma_host = current_app.config["CHROMA_HOST"]
                chroma_port = current_app.config["CHROMA_PORT"]
                logger.info(f"CHROMA_HOST IS {chroma_host}, CHROMA_PORT IS {chroma_port}")
                chroma_client = chromadb.HttpClient(
                    host=chroma_host,
                    port=chroma_port,
                    #TODO: Setup Authentication, it's not needed in a local setup though so we didn't really do it
                    settings=Settings(
                        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                        chroma_client_auth_credentials="your_secret_token_here",
                        allow_reset=True
                    )
                )
            else:
                return chroma_client
        except Exception as e:
            logger.warning(f"Failed to connect to Chroma (attempt {retries + 1}/{max_retries}): {str(e)}")
            retries += 1
            if retries < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    raise Exception("Failed to connect Chroma after multiple attempts")
    

def get_collection():
    global embedding_function
    logger.info("CALLED GET_COLLECTION")
    client = get_chroma_client()
    collection = None
    embedding_function = embedding_function or ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
    try:
        logger.info("asdf LINE 39")
        collection = client.get_collection(name="documents", embedding_function=embedding_function)
        return collection
    except Exception as e:
        logger.info("asdf LINE 42")
        logger.info(f"Collection 'documents' not found, creating it. Error: {str(e)}")
        collection = client.create_collection(name="documents", embedding_function=embedding_function)

# API ENDPOINT FUNCTION

def search_documents(query):
    """
    Search through submitted files to find the best matches for the given query.

    This function handles all POST requests to the '/search' endpoint.

    Args:
        None
    Returns:
        tuple - a dictionary of the data and the http code
        if successful: returns the results of the prompt it was given with a status code of 200
    """
    if not query:
        return jsonify({'error': 'No query given.'}), 400
    logger.debug(f"Searching documents with query: {query}")
    collection = get_collection()
    try:
        results = collection.query(
            query_texts=[query],
            n_results=5
        )
        return results, 200
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
    
