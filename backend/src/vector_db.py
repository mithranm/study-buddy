import chromadb
from flask import request, jsonify, current_app
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables to store the Embedding Function and Chroma Client so they don't get made more than once
embedding_function = None
chroma_client = None


# HELPER METHODS

def get_chroma_client():
    global chroma_client
    if chroma_client is None:
        try:
            chroma_client = chromadb.Client(
                Settings(
                    chroma_server_host=current_app.config.get('CHROMA_SERVER_HOST', 'localhost'),
                    chroma_server_http_port=current_app.config.get('CHROMA_SERVER_PORT', 9092)
                )
            )
            logger.info("ChromaDB client connected to the server.")
        except Exception as e:
            logger.error(f"Error connecting to ChromaDB server: {str(e)}")
            raise
    return chroma_client

def get_collection():
    logger.info("CALLED GET_COLLECTION")
    client = get_chroma_client()

    logger.info("GET_CHROMA_CLIENT PASSED")
    collection = client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
    )

    logger.info("GET_COLLECTION PASSED")
    return collection

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
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    
    return results, 200
