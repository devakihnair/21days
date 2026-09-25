"""Document & PDF Text Extractor for ExamPrep AI."""

import io
import re
from pathlib import Path
from typing import Union, BinaryIO

def extract_text_from_pdf(pdf_source: Union[str, Path, BinaryIO, bytes]) -> str:
    """Extracts all readable text from a PDF file path or file-like stream using pypdf."""
    from pypdf import PdfReader
    
    if isinstance(pdf_source, (str, Path)):
        reader = PdfReader(str(pdf_source))
    elif isinstance(pdf_source, bytes):
        reader = PdfReader(io.BytesIO(pdf_source))
    else:
        reader = PdfReader(pdf_source)
        
    extracted_pages = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            extracted_pages.append(f"--- [Page {idx + 1}] ---\n{text}")
            
    full_text = "\n\n".join(extracted_pages)
    return clean_extracted_text(full_text)

def clean_extracted_text(raw_text: str) -> str:
    """Cleans up excessive newlines, line breaks within sentences, and artifact spaces."""
    # Replace multiple empty lines with double newlines
    text = re.sub(r'\n{3,}', '\n\n', raw_text)
    # Replace weird non-breaking spaces or tabs
    text = text.replace('\xa0', ' ').replace('\t', ' ')
    # Normalize consecutive spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def extract_from_uploaded_file(uploaded_file) -> str:
    """Extracts text based on uploaded file extension (.pdf, .txt, .md)."""
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith((".txt", ".md")):
        bytes_data = uploaded_file.read()
        try:
            return clean_extracted_text(bytes_data.decode("utf-8"))
        except UnicodeDecodeError:
            return clean_extracted_text(bytes_data.decode("latin-1", errors="replace"))
    else:
        raise ValueError(f"Unsupported file type for '{uploaded_file.name}'. Please upload a PDF or TXT file.")
