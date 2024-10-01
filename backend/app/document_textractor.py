import sys
import os
from pathlib import Path
import pypdf
import markdown

output_dir = "./documents"

# Basic skeleton of the method. We need to modify this. xlsx, html, docx file.
def file_to_markdown(file_path):
    try:
        file_name, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == ".pdf":
            return pdf_to_markdown(file_path)
        else:
            return f"Unsupported file type: {file_extension}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def pdf_to_markdown(pdf_path):
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Extract the filename without extension
    filename = Path(pdf_path).stem

    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(file) # Reads the binary information of the pdf.
        
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

if __name__ == "__main__":

    pdf_path = sys.argv[1]

    pdf_to_markdown(pdf_path)