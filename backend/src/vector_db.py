import os
import chromadb
import requests
from flask import request, jsonify, current_app
from chromadb.utils import embedding_functions
import json
import time
import re
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')

# Global variables to store the Embedding Function and Chroma Client so they don't get made more than once
embedding_function = None
chroma_client = None
ollama_base_url = OLLAMA_HOST

if os.path.exists('/.dockerenv'):
    # Set the base URL for Ollama package
    match = re.search(r'localhost:(\d+)', OLLAMA_HOST)

    if match:
        # Extract the port number
        port = match.group(1)
        
        # Create the new host string
        ollama_base_url = f'host.docker.internal:{port}'
        
        # Set the new OLLAMA_HOST value
        os.environ['OLLAMA_HOST'] = ollama_base_url
        
        logger.info(f"Updated OLLAMA_HOST from '{OLLAMA_HOST}' to '{ollama_base_url}'")
    else:
        logger.info(f"Did not find a valid localhost:port pattern in OLLAMA_HOST: '{OLLAMA_HOST}'")

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
    client = get_chroma_client()
    embedding_func = get_embedding_function()
    collection = client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine", "hnsw:construction_ef": 100, "hnsw:search_ef": 10}
    )
    return collection

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

def chat(search_results, prompt):
    """
    Calls Ollama endpoint api/chat with text chunk + prompt given by user.

    Args:
        search_results: dictionary
        prompt: string

    Return:
        tuple - contains a json and a http code.
        if successful: return a json filled with Ollama results with the http code 200
        if ollama timeout: return ({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 504)
        if HTTPerror: return ({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 400 (maybe?))
        if RequestException: return ({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 500)
        
    """
    logger.info("Starting chat function")
    logger.info(f"Search results: {search_results}")
    logger.info(f"Prompt: {prompt}")
    
    # Extract only the documents from search_results (assume it's a list of one list)
    documents = search_results.get('documents', [[]])

    # Since documents is usually one list, let's access that directly and join with separators
    if documents and isinstance(documents[0], list):
        context = '\n\n---\n\n'.join(documents[0])  # Separate each document clearly
    else:
        context = ''
    
    logger.info(f"Constructed context: {context}")
    
    try:
        
        # Prepare the request payload
        payload = {
            "model": "llama3.2",
            "messages": [
                {
                    "role": "system",
                    "content": f"Read the sources and respond to the prompt given by the user. Sources: {context}"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "options": {
                "seed": 101,
                "temperature": 0
            }
        }

        logger.info(f"Payload sent to Ollama: {json.dumps(payload, indent=2)}")
        logger.info("Sending request to Ollama")
        start_time = time.time()

        # Send POST request to Ollama with a longer timeout
        response = requests.post(
            f'http://{ollama_base_url}/api/chat',
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        end_time = time.time()
        logger.info(f"Request completed in {end_time - start_time:.2f} seconds")

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        result = response.json()
        logger.info(f"Ollama full response: {json.dumps(result, indent=2)}")

        # Extract the 'message' field
        chatted_message = result.get('message')
        if not chatted_message:
            # Handle cases where 'message' is missing
            logger.info("No 'message' field found in Ollama response.")
            return jsonify({'error': 'No message from Ollama.'}), 500

        logger.info(f"Extracted message: {chatted_message}")

        return jsonify({'message': chatted_message}), 200

    except requests.exceptions.Timeout:
        logger.info("Request to Ollama timed out")
        return jsonify({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 504
    except requests.exceptions.HTTPError as e:
        # More detailed HTTP error handling
        logger.info(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
        return jsonify({'error': f'Ollama HTTP error: {e.response.status_code}'}), e.response.status_code
    except requests.exceptions.RequestException as e:
        logger.info(f"Ollama request failed: {e}")
        return jsonify({'error': f'Error generating response: {str(e)}'}), 500
    except KeyError as e:
        # Capture unexpected response formats
        logger.info(f"Unexpected response format: {e} - Response: {result}")
        return jsonify({'error': 'Unexpected response format from Ollama'}), 500
    except Exception as e:
        # Catch-all for any other exceptions
        logger.info(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
