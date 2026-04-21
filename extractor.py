import pdfplumber

def read_pdf(filepath):

    text = ""

    with pdfplumber.open(filepath) as pdf:
        pages = pdf.pages

        for page in pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text
