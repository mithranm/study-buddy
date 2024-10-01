from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.utils import embedding_functions
import os
import nltk
from nltk.tokenize import sent_tokenize
import threading

app = Flask(__name__)
CORS(app)

CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', '/app/chroma_db')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')

# Global variables to track initialization status
nltk_ready = False
chroma_ready = False
initialization_error = None

def initialize_backend():
    global nltk_ready, chroma_ready, initialization_error, collection
    try:
        # Initialize NLTK
        nltk.download('punkt', quiet=True)
        nltk_ready = True

        # Initialize Chroma
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        embedding_function = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_function
        )
        chroma_ready = True
    except Exception as e:
        initialization_error = str(e)

# Start initialization in a separate thread
threading.Thread(target=initialize_backend, daemon=True).start()

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'nltk_ready': nltk_ready,
        'chroma_ready': chroma_ready,
        'error': initialization_error
    })

def chunk_document(content, chunk_size=1000, overlap=200):
    sentences = sent_tokenize(content)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
            
            # Add overlap
            overlap_text = " ".join(chunks[-1].split()[-overlap:])
            current_chunk = overlap_text + " " + current_chunk
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def embed_document(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    chunks = chunk_document(content)
    collection.add(
        documents=chunks,
        ids=[f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))],
        metadatas=[{"source": file_path} for _ in chunks]
    )

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
        embed_document(filename)
        return jsonify({'message': 'File uploaded and embedded successfully'}), 200

@app.route('/search', methods=['POST'])
def search_documents():
    if not (nltk_ready and chroma_ready):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    query = request.json.get('query')
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    return jsonify(results)

@app.route('/documents', methods=['GET'])
def list_documents():
    if not (nltk_ready and chroma_ready):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    if not (nltk_ready and chroma_ready):
        return jsonify({'error': 'Backend is not fully initialized yet'}), 503
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        # Remove document chunks from Chroma
        collection.delete(where={"source": file_path})
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'error': 'Document not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    app.run(host='0.0.0.0', port=port, debug=False)