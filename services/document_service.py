import os
import PyPDF2
import docx

def extract_text(filepath):
    ext = filepath.split(".")[-1].lower()

    if ext == "pdf":
        return extract_pdf_text(filepath)
    elif ext == "docx":
        return extract_docx_text(filepath)
    elif ext == "txt":
        return extract_txt_text(filepath)
    else:
        raise ValueError("Unsupported file type")

def extract_pdf_text(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_docx_text(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_txt_text(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks (by words)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks