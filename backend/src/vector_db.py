import os
import chromadb
import ollama
from flask import request, jsonify, current_app
from chromadb.utils import embedding_functions

# Global variables to store the embedding function and Chroma client
embedding_function = None
chroma_client = None

def get_chroma_client():
    global chroma_client
    if chroma_client is None:
        # Use the app config to get the CHROMA_DB_PATH, fallback to /app/chroma_db if not set
        chroma_db_path = current_app.config.get('CHROMA_DB_PATH', '/app/chroma_db')
        chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    return chroma_client

def get_embedding_function():
    global embedding_function
    if embedding_function is None:
        embedding_function = embedding_functions.DefaultEmbeddingFunction()
    return embedding_function

def get_collection():
    client = get_chroma_client()
    embedding_func = get_embedding_function()
    collection = client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_func,
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
    print(jsonify(results))
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
    
    # response = ollama.chat(model='llama3.2:3b', messages=[
    # {
    #     'role': 'user',
    #     'content': 'Why is the sky blue?',
    # },
    # ])
    # return jsonify(response['message']), 200