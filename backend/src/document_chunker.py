import os
from nltk.tokenize import sent_tokenize
from pathlib import Path
from . import document_textractor as textractor

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

def embed_documents(file_paths, collection):
    all_chunks = []
    all_ids = []
    all_metadatas = []
    for file_path in file_paths:
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            # Use file_to_markdown for other file types
            content = textractor.file_to_markdown(file_path)
            
            # If file_to_markdown returns an error message, skip this file
            if content.startswith("Unsupported file type") or content.startswith("File not found") or content.startswith("An error occurred"):
                print(f"Skipping {file_path}: {content}")
                continue
        
        chunks = chunk_document(content)
        all_chunks.extend(chunks)
        all_ids.extend([f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))])
        all_metadatas.extend([{"source": file_path} for _ in chunks])
    
    collection.add(
        documents=all_chunks,
        ids=all_ids,
        metadatas=all_metadatas
    )

    return collection