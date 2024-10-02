from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import nltk
import threading
import ollama
import logging

# Project python files.
# Project python files.
from . import document_chunker as chunker
from . import vector_db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure CHROMA_DB_PATH is set in the config
    app.config.setdefault('CHROMA_DB_PATH', '/app/chroma_db')
    app.config.setdefault('UPLOAD_FOLDER', '/app/uploads')
    app.config.setdefault('RAW_DOCUMENTS_PATH', '/app/raw-documents')

    # Log all app configurations
    for key, value in app.config.items():
        logger.debug(f"App config: {key} = {value}")

    # Ensure the required directories exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CHROMA_DB_PATH'], exist_ok=True)
        os.makedirs(app.config['RAW_DOCUMENTS_PATH'], exist_ok=True)
        logger.info("Created necessary directories")
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")

    # Ensure the upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', '/app/uploads'), exist_ok=True)

    # Global variables to track initialization status
    app.nltk_ready = False
    app.chroma_ready = False
    app.initialization_error = None

    def is_ready():
        return app.nltk_ready and app.chroma_ready

    def initialize_backend():
        try:
            # Initialize ollama
            ollama.pull('llama3.2:3b')
            
            # Initialize NLTK
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            app.nltk_ready = True

            # Initialize Chroma collection
            vector_db.get_collection()
            app.chroma_ready = True
        except Exception as e:
            app.initialization_error = str(e)

    # Start initialization in a separate thread
    threading.Thread(target=initialize_backend, daemon=True).start()

    @app.route('/status', methods=['GET'])
    def get_status():
        return jsonify({
            'nltk_ready': app.nltk_ready,
            'chroma_ready': app.chroma_ready,
            'error': app.initialization_error
        })

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if not is_ready():
            return jsonify({'error': 'Backend is not fully initialized yet'}), 503
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            collection = vector_db.get_collection()
            chunker.embed_documents([filename], collection)
            return jsonify({'message': 'File uploaded and embedded successfully'}), 200

    @app.route('/search', methods=['POST'])
    def search_wrapper():
        if not is_ready():
            return jsonify({'error': 'Backend is not fully initialized yet'}), 503
        return vector_db.search_documents()

    @app.route('/documents', methods=['GET'])
    def list_documents():
        if not is_ready():
            return jsonify({'error': 'Backend is not fully initialized yet'}), 503
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify(files)

    @app.route('/documents/<filename>', methods=['DELETE'])
    def delete_document(filename):
        if not is_ready():
            return jsonify({'error': 'Backend is not fully initialized yet'}), 503
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
        if not is_ready():
            return jsonify({'error': 'Backend is not fully initialized yet'}), 503
        return vector_db.generate()

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    app.run(host='0.0.0.0', port=port, debug=False)