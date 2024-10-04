import os
import re
import logging
import requests
import time
from flask import jsonify
import json

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')
ollama_base_url = OLLAMA_HOST
if os.path.exists('/.dockerenv'):
    # Set the base URL for Ollama package
    match = re.search(r'localhost:(\d+)', OLLAMA_HOST)

    if match:
        # Extract the port number
        port = match.group(1)
        
        # Create the new host string with 'http://'
        ollama_base_url = f'http://host.docker.internal:{port}'
        
        # Set the new OLLAMA_HOST value
        os.environ['OLLAMA_HOST'] = ollama_base_url
        
        logger.info(f"Updated OLLAMA_HOST from 'http://{OLLAMA_HOST}' to '{ollama_base_url}'")
    else:
        logger.info(f"Did not find a valid localhost:port pattern in OLLAMA_HOST: '{OLLAMA_HOST}'")

def ollama_health_check():
    """
    Check if Ollama is running by sending a GET request to the root endpoint.

    Args:
        None

    Returns:
        bool: True if Ollama is running and accessible, False otherwise.

    """
    try:
        response = requests.get(f"{ollama_base_url}", timeout=3)

    except Exception as e:
        logger.error(f"Error: {e}")
        return False
    if response.status_code == 200:
        return True
    
def get_models():
    """
    Gets the models available on your local machine.

    Args:
        None

    Returns:
        tuple - a json and a status code
        if successful: ({'models': String[]}, 200)
    """

    models = []

    try:
        response = requests.get(f"{ollama_base_url}/api/tags")
        
        result = response.json()
        # Parsing through json to get model names only.

        for model in result.get('models'):
            models.append(model.name)

        return jsonify({'models': models}), 200

    except Exception as e:
        logger.info(f"Error at get_models: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    

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
            "model": "llama3.2:3b", # why was this llama3.2? thought we were using llama3.2:3b
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
            # DELETED OPTIONS WITH TEMPATURE
        }

        logger.info(f"Payload sent to Ollama: {json.dumps(payload, indent=2)}")
        logger.info("Sending request to Ollama")
        logger.info(f"Ollama base url {ollama_base_url}")
        start_time = time.time()

        # Send POST request to Ollama with a longer timeout
        response = requests.post(
            f'{ollama_base_url}/api/chat',
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

        logger.info(f"Extracted message: {chatted_message['content']}")

        return jsonify({'message': chatted_message['content']}), 200 # do we want to do this instead? check the frontend to see the format. All i did was indexed it to only get the content.

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
