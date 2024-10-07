import os
import nltk
import logging
import traceback
import sys
import time
from flask import Flask, request, jsonify, Blueprint, current_app
from flask_cors import CORS
from celery import Celery, Task
import redis

# Project python files.
from . import document_chunker as chunker
from . import vector_db
from . import ollama_calls as ollama
from .tasks import process_file
from . import make_celery
from werkzeug.utils import secure_filename

# BLUEPRINT OF API
bp = Blueprint('study-buddy', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("gunicorn").setLevel(logging.WARNING)


# API ENDPOINT METHODS HERE
@bp.route('/status', methods=['GET'])
def get_status():
    """
    Endpoint to check the status of the backend.
    """
    return jsonify({
        'nltk_ready': current_app.nltk_ready,
        'chroma_ready': current_app.chroma_ready,
        'error': current_app.initialization_error
    })

@bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Uploads a file and processes it asynchronously.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        collection = vector_db.get_collection()
        if os.path.exists(file_path) and len(collection.get(where={"source": file_path})['ids']):
            return jsonify({"error": "File already exists."}), 400

        file.save(file_path)

        # Enqueue the task
        task = process_file.delay(file_path, current_app.config["TEXTRACTED_PATH"])

        return jsonify({'message': 'File received and is being processed', 'task_id': task.id}), 202

@bp.route('/task_status/<task_id>')
def task_status(task_id):
    """
    Retrieves the status of a Celery task.
    """
    task = current_app.celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'STARTED':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info.get('status', '')),
            'traceback': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
    return jsonify(response)


@bp.route('/search', methods=['POST'])
def search_wrapper():
    """
    Search through submitted files to find the best matches for the given query. This is a wrapper to vector_db.search_documents()

    This function handles all POST requests to the '/search' endpoint.

    Args:
        None
    Returns:
        tuple - a json of the data and the http code
        if backend not ready: returns ({'error': 'Backend is fully initialized yet'}), 503)
    """
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    return vector_db.search_documents(query)

@bp.route('/documents', methods=['GET'])
def list_documents():
    """
    Retrieve all documents and return it back to the frontend in json format to be displayed on the screen.

    This function handles all GET requests to '/documents' endpoint.

    Args:
        None
    Returns:
        tuple: a json file that contains data and http code
        if successful: sends a json of the files submitted with the http code 200.
        if backend not ready: ({error: Backend is fully initialized yet}, 503).

    Raises:
        None
    """
    files = os.listdir(current_app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@bp.route('/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """
    Delete a document and its associated chunks from the system.

    This function handles HTTP DELETE requests to remove a specific document
    identified by its filename. It also removes the corresponding document
    chunks from the Chroma vector store.

    Args:
        filename (str): The name of the file to be deleted.

    Returns:
        tuple: A tuple containing a JSON response and an HTTP status code.
            - If successful: ({'message': 'Document deleted successfully'}, 200)
            - If backend not ready: ({'error': 'Backend is not fully initialized yet'}, 503)
            - If file not found: ({'error': 'Document not found'}, 404)

    Raises:
        None
    """
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename) 
    if os.path.exists(file_path):
        # Remove document chunks from Chroma
        collection = vector_db.get_collection()
        collection.delete(where={"source": file_path})

        # Remove from backend/upload/
        os.remove(file_path)
        
        split_filename = os.path.splitext(filename)
        if (split_filename[1] == ".pdf"):
            textracted_path = os.path.join(current_app.config['TEXTRACTED_PATH'], f"{split_filename[0]}.md")

            os.remove(textracted_path)

        logger.info(f"New collection file should not be present: {collection.peek(100)['ids']}") # after deletion you should not see the file in the database you just deleted.
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'error': 'Document not found'}), 404
    
@bp.route('/get_models', methods=['GET'])
def get_models_wrapper():
    """
    Add pydocs here :p
    """
    if (not ollama.ollama_health_check()):
        logger.info("Ollama is not running")
        return jsonify({'error': 'Ollama is not running, please make sure ollama is running on your local machine'}, 503)
    
    return ollama.get_models()


@bp.route('/chat', methods=['POST'])
def chat_wrapper():
    """
    chat an LLM response from the prompt in the request body and chunks from documents already uploaded.

    Args:
        None

    Returns:
        tuple: A tuple containing a JSON response and an HTTP status code.
    Raises:
        None
    """

    if (not ollama.ollama_health_check()):
        logger.info("Ollama is not running")
        return jsonify({'error': 'Ollama is not running, please make sure ollama is running on your local machine'}, 503)
    
    prompt = request.json.get('prompt')

    model = request.json.get('model')

    if not prompt:
        return jsonify({'error': 'No prompt given'}), 400

    try:
        print("running search documents")
        search_results, http_code = vector_db.search_documents(prompt)

        if http_code != 200:
            return jsonify({'error': 'Search failed'}), http_code
        
        # Call chat with the search results and prompt
        return ollama.chat(search_results, prompt, model)
    except Exception as e:
        print("Exception chat")
        traceback.print_exc(file=sys.stderr)
        return jsonify({'error': f'Exception in chat process: {str(e)}'}), 500

def initialize_chroma():
    client = vector_db.get_chroma_client()
    try:
        # Attempt to create the default tenant and database
        client.create_tenant("default_tenant")
        client.create_database("default_database", "default_tenant")
    except Exception as e:
        # If tenant/database already exists, this will throw an exception
        logger.info(f"Tenant/Database initialization: {str(e)}")
    
    # Now get or create your collection
    collection = vector_db.get_collection()
