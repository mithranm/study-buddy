from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.utils import embedding_functions
import os
import nltk
import threading

# Project python files.
import document_chunker as chunker

app = Flask(__name__)
CORS(app)

CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', '/app/chroma_db')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')

# Global variables to track initialization status
nltk_ready = False
chroma_ready = False
initialization_error = None

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

def initialize_backend():
    global nltk_ready, chroma_ready, initialization_error
    try:
        # Initialize NLTK
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        nltk_ready = True

        # Initialize Chroma collection
        get_collection()
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
    if not (nltk_ready and chroma_ready):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        collection = get_collection()
        chunker.embed_documents([filename], collection)  # Call embed_documents with a list containing the filename
        return jsonify({'message': 'File uploaded and embedded successfully'}), 200

@app.route('/search', methods=['POST'])
def search_documents():
    """
    Search through submitted files to find the best matches for the given query. WE MIGHT GET RID OF THIS ENDPOINT LATER.

    This function handles all POST requests to the '/search' endpoint.
    
    Args:
        None
    Returns:
        tuple - a json of the data and the http code
        if successful: returns the results of the prompt it was given with a status code of 200

    """
    if not (nltk_ready and chroma_ready):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    collection = get_collection()
    query = request.json.get('query')
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    return jsonify(results)

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
    if not (nltk_ready and chroma_ready):
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
    if not (nltk_ready and chroma_ready):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        # Remove document chunks from Chroma
        collection = get_collection()
        collection.delete(where={"source": file_path})
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'error': 'Document not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    app.run(host='0.0.0.0', port=port, debug=False)