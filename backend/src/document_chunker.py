import os
import re
import io
import uuid
import logging
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from nltk.tokenize import sent_tokenize
import chromadb

from . import google_calls
from . import document_textractor

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Adjust as needed

# Create formatter and add it to the handlers
formatter = logging.Formatter('[%(levelname)s] %(message)s')
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(ch)

# Constants
MAX_IMAGE_SIZE = (1000, 1000)  # Maximum width and height for images
IMAGE_DIR_NAME = "extracted_images"  # Directory to save extracted images
CAPTION_START = "[[IMAGE_CAPTION_START]]"
CAPTION_END = "[[IMAGE_CAPTION_END]]"
ALLOWED_FILE_EXTENSIONS = {'.txt', '.md', '.pdf'}  # Allowed file types
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB max file size

def ensure_image_dir(base_path: str) -> str:
    """
    Ensure the image directory exists within the given base path.

    Args:
        base_path (str): The base directory path.

    Returns:
        str: The full path to the image directory.
    """
    image_path = os.path.join(base_path, IMAGE_DIR_NAME)
    os.makedirs(image_path, exist_ok=True)
    logger.debug(f"Ensured image directory exists at: {image_path}")
    return image_path

def scale_image(image_bytes: bytes) -> bytes:
    """
    Scale the image to a maximum size while maintaining aspect ratio.

    Args:
        image_bytes (bytes): The original image bytes.

    Returns:
        bytes: The scaled image bytes in JPEG format.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
            output = io.BytesIO()
            img.save(output, format='JPEG')
            scaled_bytes = output.getvalue()
            logger.debug("Image scaled successfully.")
            return scaled_bytes
    except Exception as e:
        logger.error(f"Failed to scale image: {e}")
        raise

def chunk_document(content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Chunks the document while respecting image captions.
    Ensures that caption start and end markers are always in the same chunk.

    Args:
        content (str): The full text content of the document.
        chunk_size (int): Maximum number of characters per chunk.
        overlap (int): Number of overlapping characters between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    logger.debug("Starting document chunking.")
    # Define a regex pattern to match image captions
    caption_pattern = re.escape(CAPTION_START) + r'.*?' + re.escape(CAPTION_END)

    # Split the content into parts, separating captions and other text
    parts = re.split(f'({caption_pattern})', content, flags=re.DOTALL)

    chunks = []
    current_chunk = ""

    for part in parts:
        if re.match(caption_pattern, part):
            # Always start a new chunk for captions if the current chunk is not empty
            if current_chunk:
                chunks.append(current_chunk.strip())
                logger.debug(f"Added chunk without caption. Current chunk size: {len(current_chunk)}")
                current_chunk = ""
            
            # Add the entire caption as a single chunk
            chunks.append(part.strip())
            logger.debug(f"Added chunk with caption. Caption length: {len(part)}")
        else:
            sentences = sent_tokenize(part)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= chunk_size:
                    current_chunk += sentence + " "
                else:
                    chunks.append(current_chunk.strip())
                    logger.debug(f"Added chunk during sentence processing. Current chunk size: {len(current_chunk)}")
                    # Add overlap based on characters
                    overlap_text = current_chunk[-overlap:].strip()
                    current_chunk = overlap_text + " " + sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())
        logger.debug(f"Added final chunk. Final chunk size: {len(current_chunk)}")

    # Log chunk information
    for i, chunk in enumerate(chunks):
        if CAPTION_START in chunk and CAPTION_END in chunk:
            logger.info(f"Chunk {i} contains complete caption.")
        elif CAPTION_START in chunk or CAPTION_END in chunk:
            logger.warning(f"Chunk {i} contains incomplete caption markers.")
        else:
            logger.info(f"Chunk {i} does not contain caption.")

    logger.debug("Document chunking completed.")
    return chunks

def process_pdf_with_captions(file_path: str, textracted_path: str) -> str:
    """
    Processes a PDF file to extract text and images, generates captions for images,
    and inserts captions into the extracted text.

    Args:
        file_path (str): The path to the PDF file.
        textracted_path (str): The base path for extracted content.

    Returns:
        str: The full text content with image captions inserted.
    """
    logger.info(f"Starting processing of PDF: {file_path}")
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        logger.error(f"Failed to open PDF file {file_path}: {e}")
        return ""

    full_text = ""
    image_dir = ensure_image_dir(textracted_path)

    for page_num, page in enumerate(doc, start=1):
        logger.debug(f"Processing page {page_num}")
        blocks = page.get_text("dict")["blocks"]
        elements = []

        for block in blocks:
            block_type = block.get("type")
            if block_type == 0:  # Text block
                text = block.get("text", "").strip()
                if text:
                    elements.append({
                        "type": "text",
                        "y0": block["bbox"][1],
                        "content": text
                    })
            elif block_type == 1:  # Image block
                img = block.get("image")
                if img is None:
                    logger.warning(f"No image data found in image block on page {page_num}")
                    continue

                logger.debug(f"Image block on page {page_num}: {img}")
                logger.debug(f"Type of image block: {type(img)}")

                if isinstance(img, dict):
                    xref = img.get("xref")
                    if xref is None:
                        logger.error(f"No 'xref' found in image block on page {page_num}")
                        continue
                    elements.append({
                        "type": "image",
                        "y0": block["bbox"][1],
                        "xref": xref
                    })
                elif isinstance(img, bytes):
                    # Handle bytes image data
                    logger.debug(f"Image data (bytes) on page {page_num}: {img[:20]}...")  # Log first 20 bytes
                    try:
                        image = Image.open(io.BytesIO(img))
                        # Save the image securely
                        image_filename = f"{uuid.uuid4()}.jpeg"
                        image_path = os.path.join(image_dir, image_filename)
                        image.save(image_path, "JPEG")
                        logger.debug(f"Saved image to {image_path}")

                        # Generate caption
                        caption = google_calls.caption_image(image_path)
                        caption_text = f"{CAPTION_START}{caption}{CAPTION_END}"
                        full_text += caption_text + "\n"
                        logger.info(f"Added caption for image on page {page_num}: {caption}")

                        # Perform OCR on the image
                        ocr_text = pytesseract.image_to_string(image).strip()
                        if ocr_text:
                            full_text += ocr_text + "\n"
                            logger.info(f"Added OCR text from image on page {page_num}: {ocr_text[:100]}...")
                        else:
                            logger.warning(f"No text extracted via OCR from image on page {page_num}")
                    except Exception as e:
                        logger.error(f"Failed to process image bytes on page {page_num}: {e}")
                        full_text += f"{CAPTION_START}Image processing failed{CAPTION_END}\n"
                else:
                    logger.error(f"Unexpected image block format on page {page_num}: {type(img)}")
            else:
                logger.debug(f"Unknown block type {block_type} on page {page_num}")

        # Log the number of elements found on the page
        num_text = sum(1 for el in elements if el["type"] == "text")
        num_images = sum(1 for el in elements if el["type"] == "image")
        logger.debug(f"Page {page_num}: Found {num_text} text blocks and {num_images} image blocks")

        # If no text blocks, perform OCR on the entire page
        if num_text == 0:
            logger.debug(f"No text blocks found on page {page_num}. Performing OCR on entire page.")
            try:
                pix = page.get_pixmap()
                img_data = pix.pil_tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                ocr_text = pytesseract.image_to_string(image).strip()
                if ocr_text:
                    full_text += ocr_text + "\n"
                    logger.info(f"Added OCR text from entire page {page_num}: {ocr_text[:100]}...")
                else:
                    logger.warning(f"No text extracted via OCR from entire page {page_num}")
            except Exception as e:
                logger.error(f"Failed to perform OCR on entire page {page_num}: {e}")

        # Sort elements by their vertical position (y0)
        elements.sort(key=lambda el: el["y0"])

        for element in elements:
            if element["type"] == "text":
                full_text += element["content"] + "\n"
                logger.debug(f"Appended text block: {element['content'][:100]}...")
            elif element["type"] == "image":
                xref = element["xref"]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                except Exception as e:
                    logger.error(f"Failed to extract image xref {xref} on page {page_num}: {e}")
                    full_text += f"{CAPTION_START}Image extraction failed{CAPTION_END}\n"
                    continue

                # Scale image
                try:
                    scaled_image_bytes = scale_image(image_bytes)
                except Exception as e:
                    logger.error(f"Scaling failed for image xref {xref} on page {page_num}: {e}")
                    full_text += f"{CAPTION_START}Image scaling failed{CAPTION_END}\n"
                    continue

                # Save image securely
                image_filename = f"{uuid.uuid4()}.jpeg"
                image_path = os.path.join(image_dir, image_filename)
                try:
                    with open(image_path, 'wb') as img_file:
                        img_file.write(scaled_image_bytes)
                    logger.debug(f"Saved scaled image to {image_path}")
                except Exception as e:
                    logger.error(f"Failed to save image {image_path} on page {page_num}: {e}")
                    full_text += f"{CAPTION_START}Image saving failed{CAPTION_END}\n"
                    continue

                # Generate caption
                try:
                    caption = google_calls.caption_image(image_path)
                    caption_text = f"{CAPTION_START}{caption}{CAPTION_END}"
                    full_text += caption_text + "\n"
                    logger.info(f"Added caption for image xref {xref} on page {page_num}: {caption}")
                except Exception as e:
                    logger.error(f"Error captioning image xref {xref} on page {page_num}: {e}")
                    # Insert a placeholder if captioning fails
                    full_text += f"{CAPTION_START}Image caption unavailable{CAPTION_END}\n"

        logger.info(f"Processed page {page_num} of {file_path}")

    logger.info(f"Processed PDF: {file_path}")
    logger.debug(f"Full text content after processing:\n{full_text}")
    return full_text

def embed_documents(file_paths: List[str], collection: chromadb.Collection, textracted_path: str) -> None:
    """
    Populates a ChromaDB collection with embeddings from an array of documents.

    Args:
        file_paths (List[str]): A list of file paths to the documents.
        collection (chromadb.Collection): The ChromaDB collection to populate.
        textracted_path (str): The path to the textracted output.

    Returns:
        None
    """
    logger.info("Starting embedding of documents.")
    all_chunks = []
    all_ids = []
    all_metadatas = []

    for file_path in file_paths:
        file_extension = Path(file_path).suffix.lower()

        # Security: Validate file extension
        if file_extension not in ALLOWED_FILE_EXTENSIONS:
            logger.warning(f"Skipping unsupported file type {file_extension} for file {file_path}.")
            continue

        # Security: Validate file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                logger.warning(f"Skipping file {file_path} due to size {file_size} exceeding limit.")
                continue
        except Exception as e:
            logger.error(f"Could not get file size for {file_path}: {e}")
            continue

        content = ""

        if file_extension in ['.txt', '.md']:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                logger.debug(f"Read content from text file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to read text file {file_path}: {e}")
                continue
        elif file_extension == '.pdf':
            content = process_pdf_with_captions(file_path, textracted_path)
        else:
            try:
                # Implement your own file_to_markdown conversion if needed
                converted_path = textractor.file_to_markdown(file_path, textracted_path)
                with open(converted_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                logger.debug(f"Converted file to markdown and read content: {converted_path}")
            except Exception as e:
                logger.error(f"Skipping {file_path}: {str(e)}")
                continue

        if not content.strip():
            logger.warning(f"No content extracted from {file_path}. Skipping chunking.")
            continue

        logger.info(f"Content before chunking for {file_path}:\n{content[:1000]}")  # Log first 1000 characters
        chunks = chunk_document(content)

        if not chunks:
            logger.warning(f"No chunks created from {file_path}. Skipping embedding.")
            continue

        # Log and verify chunks contain captions
        for i, chunk in enumerate(chunks):
            if CAPTION_START in chunk and CAPTION_END in chunk:
                logger.info(f"Chunk {i} from {file_path} contains caption.")
            else:
                logger.info(f"Chunk {i} from {file_path} does not contain caption.")

        all_chunks.extend(chunks)
        all_ids.extend([f"{Path(file_path).stem}_{i}" for i in range(len(chunks))])
        all_metadatas.extend([{"source": file_path} for _ in chunks])

    if not all_chunks:
        logger.warning("No chunks to add to ChromaDB collection.")
        return

    logger.info(f"Adding {len(all_chunks)} chunks to ChromaDB collection.")
    try:
        collection.add(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadatas
        )
        logger.info("Finished adding chunks to ChromaDB collection.")
    except Exception as e:
        logger.error(f"Failed to add chunks to ChromaDB collection: {e}")

# Example of how to initialize and use the embed_documents function
if __name__ == "__main__":
    from chromadb.config import Settings

    # Initialize ChromaDB client
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_db"
    ))

    # Create or get a collection
    collection = client.get_or_create_collection(name="documents")

    # Define paths
    textracted_path = "/path/to/textracted/output"  # Update this path accordingly
    file_paths = ["/path/to/your/document.pdf"]  # Update with your document paths

    # Embed documents
    embed_documents(file_paths, collection, textracted_path)
