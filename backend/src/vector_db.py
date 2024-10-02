import os
import chromadb
import requests
from flask import request, jsonify
from chromadb.utils import embedding_functions

CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', '/app/chroma_db')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')

# Initialize embedding function and Chroma client at module level
embedding_function = embedding_functions.DefaultEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_collection():
    collection = chroma_client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
    )

    return collection


def search_documents():
    """
    Search through submitted files to find the best matches for the given query.

    This function handles all POST requests to the '/search' endpoint.

    Args:
        None
    Returns:
        tuple - a json of the data and the http code
        if successful: returns the results of the prompt it was given with a status code of 200
    """
    collection = get_collection()
    query = request.json.get('query')
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    return jsonify(results)

def generate(search_results, prompt):
    """
    Calls ollama endpoint api/generate with text chunk + prompt given by user.

    Args:
        search_results: json
        prompt: string

    Return:
        tuple - contains a json and a http code.
        if successful: pass a json filled with ollama results with the http code 200
    """
    

    response = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": OLLAMA_MODEL,
        "prompt": prompt, # stringify search_results json?

    })
