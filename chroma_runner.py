import chromadb
from chromadb.utils import embedding_functions
import os
import document_textractor as textractor

# Initialize a persistent client
client = chromadb.PersistentClient(path="./chroma_db")

# Create an embedding function (using default all-MiniLM-L6-v2 model)
embedding_function = embedding_functions.DefaultEmbeddingFunction()

# Create or get a collection
collection = client.get_or_create_collection(
    name="aws_whitepapers",
    embedding_function=embedding_function
)

def embed_document(file_path):
    # Read the document
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Split the content into chunks (you may need a more sophisticated chunking method)
    chunks = content.split('\n\n')
    
    # Embed and add chunks to the collection
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{os.path.basename(file_path)}_{i}"],
            metadatas=[{"source": file_path}]
        )

# Example usage
embed_document("path/to/aws_whitepaper.txt")

# Query example
results = collection.query(
    query_texts=["Tell me about AWS security best practices"],
    n_results=5
)
print(results)