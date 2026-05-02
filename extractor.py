"""
extractor.py — Text Extraction Module
--------------------------------------
Extracts plain text from a PDF file using PyMuPDF (fitz).
Chosen for speed, reliability, and zero external binary dependencies.

Install: pip install pymupdf
"""

import fitz  # PyMuPDF
import re


def extract_text(pdf_path: str) -> str:
    """
    Extract and clean plain text from a PDF file.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        A cleaned string of all text found in the PDF.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid PDF or has no extractable text.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Could not open PDF file: {e}")

    if doc.page_count == 0:
        raise ValueError("The PDF has no pages.")

    pages_text = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")  # plain text extraction
        if text.strip():
            pages_text.append(text)

    doc.close()

    if not pages_text:
        raise ValueError(
            "No extractable text found. The PDF may be image-based or scanned."
        )

    raw_text = "\n".join(pages_text)
    return _clean_text(raw_text)


def _clean_text(text: str) -> str:
    """
    Remove excessive whitespace, fix line breaks, and normalize unicode.

    Args:
        text: Raw extracted text string.

    Returns:
        Cleaned text string.
    """
    # Normalize unicode characters (curly quotes, dashes, etc.)
    replacements = {
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u00a0": " ",  # non-breaking space
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Remove excessive blank lines (keep at most 2 newlines in a row)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing spaces on each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()
