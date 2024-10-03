import sys
import os
from pathlib import Path
import pypdf
import markdown
import logging

logger = logging.getLogger(__name__)

def file_to_markdown(file_path, output_dir):
    try:
        file_name, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == ".pdf":
            return pdf_to_markdown(file_path, output_dir)
        else:
            logger.error(f"Unsupported file type: {file_extension}")
            raise ValueError(f"Unsupported file type: {file_extension}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise Exception

def pdf_to_markdown(pdf_path, output_dir):
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Extract the filename without extension
    filename = Path(pdf_path).stem

    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # Convert extracted text to markdown
    md = markdown.markdown(text)

    # Write markdown to file
    output_path = Path(output_dir) / f"{filename}.md"
    with open(output_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md)

    print(f"Converted {pdf_path} to {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python document_textractor.py <pdf_path> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    pdf_to_markdown(pdf_path, output_dir)