import os
import nltk
import logging
import traceback
import sys
from flask import Flask, request, jsonify, Blueprint, current_app
from flask_cors import CORS

# Project python files.
from . import document_chunker as chunker
from . import vector_db
from . import ollama_calls as ollama

# BLUEPRINT OF API
bp = Blueprint('study-buddy', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API ENDPOINT METHODS HERE
@bp.route('/status', methods=['GET'])
def get_status():
    """
    Getter method for status of backend to let any application using this interface know when its ready.

    Args:
        None

    Returns:
        json - containing nltk and chroma status variables.
    """
    return jsonify({
        'nltk_ready': current_app.nltk_ready,
        'chroma_ready': current_app.chroma_ready,
        'error': current_app.initialization_error
    })

@bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Uploads a file that is chosen by the user.

    This function handles all POST request to the '/upload' endpoint.

    Args:
        None
    Returns:
        tuple - a json of the message and the http code
        if successful: ({'message': 'File uploaded and embedded sucessfully'}, 200)
        if backend not ready: ({'error': 'Backend is not fully initialized yet'}, 503)
        if theres no file to upload: ({'error': 'No file part'}, 400)
        if filename is empty: ({'error': 'No selected file'}, 400)
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        collection = vector_db.get_collection()
        # Pass the TEXTRACTED_PATH to embed_documents
        chunker.embed_documents([filename], collection, current_app.config['TEXTRACTED_PATH'])
        return jsonify({'message': 'File uploaded and embedded successfully'}), 200

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
    collection = vector_db.get_collection() # TODO: get rid of this later.
    logger.info(f"State check of database: {collection.peek(100)['ids']}") # TODO: Here too
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

def create_app(test_config=None):
    """
    Creates the app.
    """
    app = Flask(__name__)
    CORS(app)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Set base_path to the project root directory
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Set default configurations
    app.config.setdefault('CHROMA_DB_PATH', os.path.join(base_path, 'chroma_db'))
    app.config.setdefault('UPLOAD_FOLDER', os.path.join(base_path, 'uploads'))
    app.config.setdefault('TEXTRACTED_PATH', os.path.join(base_path, 'textracted'))

    # Log all app configurations
    for key, value in app.config.items():
        logger.debug(f"App config: {key} = {value}")

    # Ensure the required directories exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CHROMA_DB_PATH'], exist_ok=True)
        os.makedirs(app.config['TEXTRACTED_PATH'], exist_ok=True)
        logger.info("Created necessary directories")
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")

    # Global variables to track initialization status
    app.nltk_ready = False
    app.chroma_ready = False
    app.initialization_error = None

    with app.app_context():
        try:
            # Initialize NLTK
            nltk.download('punkt_tab')
            app.nltk_ready = True

            # Initialize Chroma collection
            vector_db.get_collection()
            app.chroma_ready = True
        except LookupError as le:
            app.initialization_error = f"NLTK LookupError: {str(le)}"
            logger.error(f"Initialization error: {str(le)}")
        except Exception as e:
            app.initialization_error = f"General Initialization Error: {str(e)}"
            logger.error(f"Initialization error: {str(e)}")

    app.register_blueprint(bp, url_prefix="/api/")

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    app.run(host='0.0.0.0', port=port, debug=False)
