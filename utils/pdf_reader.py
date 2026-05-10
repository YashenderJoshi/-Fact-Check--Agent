"""
utils/pdf_reader.py
Extract raw text from uploaded PDF using PyMuPDF (fitz).
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Accepts a Streamlit UploadedFile object.
    Returns the full text content as a single string.
    """
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages_text.append(f"[Page {page_num + 1}]\n{text.strip()}")

    doc.close()
    return "\n\n".join(pages_text)
