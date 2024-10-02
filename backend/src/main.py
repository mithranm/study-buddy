from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import nltk
import threading

# Project python files.
import document_chunker as chunker
import vector_db as vector_db

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')

# Global variables to track initialization status
nltk_ready = False
chroma_ready = False
initialization_error = None

def is_ready():
    return (nltk_ready and chroma_ready)

def initialize_backend():
    try:
        # Initialize NLTK
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        nltk_ready = True

        # Initialize Chroma collection
        vector_db.get_collection()
        chroma_ready = True
    except Exception as e:
        initialization_error = str(e)

# Start initialization in a separate thread
threading.Thread(target=initialize_backend, daemon=True).start()

# ----- API END POINTS -----

# 
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'nltk_ready': nltk_ready,
        'chroma_ready': chroma_ready,
        'error': initialization_error
    })

@app.route('/upload', methods=['POST'])
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
    if not (is_ready()):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        collection = vector_db.get_collection()
        chunker.embed_documents([filename], collection)  # Call embed_documents with a list containing the filename
        return jsonify({'message': 'File uploaded and embedded successfully'}), 200

@app.route('/search', methods=['POST'])
def search_wrapper():
    """
    Search through submitted files to find the best matches for the given query. This is a wrapper to vector_db.search_documents()

    This function handles all POST requests to the '/search' endpoint.

    Args:
        None
    Returns:
        tuple - a json of the data and the http code
        if backend not ready: returns ({'error': 'Backend is not fully initialized yet'}), 503)
    """
    if not (is_ready()):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    return vector_db.search_documents()

@app.route('/documents', methods=['GET'])
def list_documents():
    """
    Retrieve all documents and return it back to the frontend in json format to be displayed on the screen.

    This function handles all GET requests to '/documents' endpoint.

    Args:
        None
    Returns:
        tuple: a json file that contains data and http code
        if successful: sends a json of the files submitted with the http code 200.
        if backend not ready: ({error: Backend is not fully initialized yet}, 503).
    
    Raises:
        None
    """
    if not (is_ready()):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/documents/<filename>', methods=['DELETE'])
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
    if not (is_ready()):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        # Remove document chunks from Chroma
        collection = vector_db.get_collection()
        collection.delete(where={"source": file_path})
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'error': 'Document not found'}), 404

@app.route('/generate', methods=['POST'])
def generate_wrapper():
    # add docs here!
    if not (is_ready()):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    vector_db.generate()

    
if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    app.run(host='0.0.0.0', port=port, debug=False)