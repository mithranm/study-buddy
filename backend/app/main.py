# Backend (Flask)
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.utils import embedding_functions
import os

app = Flask(__name__)
CORS(app)

CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH')
RAW_DOCUMENTS_PATH = os.getenv('RAW_DOCUMENTS_PATH')

# Initialize Chroma client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
embedding_function = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_function
)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
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

def embed_document(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    chunks = content.split('\n\n')
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{os.path.basename(file_path)}_{i}"],
            metadatas=[{"source": file_path}]
        )

@app.route('/search', methods=['POST'])
def search_documents():
    query = request.json.get('query')
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 9090))
    app.run(host='0.0.0.0', port=port, debug=True)