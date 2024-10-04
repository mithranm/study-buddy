import chromadb
from flask import request, jsonify, current_app
from chromadb.utils import embedding_functions
import logging

logger = logging.getLogger(__name__)

# Global variables to store the Embedding Function and Chroma Client so they don't get made more than once
embedding_function = None
chroma_client = None


# HELPER METHODS

def get_chroma_client():
    global chroma_client
    if chroma_client is None:
        chroma_db_path = current_app.config.get('CHROMA_DB_PATH', '/app/chroma_db')
        try:
            chroma_client = chromadb.PersistentClient(path=chroma_db_path)
            logger.info(f"ChromaDB client initialized with path: {chroma_db_path}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    return chroma_client

def get_embedding_function():
    global embedding_function
    if embedding_function is None:
        embedding_function = embedding_functions.DefaultEmbeddingFunction()
    return embedding_function

def get_collection():
    """
    Getter method to get the collection from the database this API is using.

    Args:
        None

    Returns:
        the collection of the database.
    """
    client = get_chroma_client()
    embedding_func = get_embedding_function()
    collection = client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
    )
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
