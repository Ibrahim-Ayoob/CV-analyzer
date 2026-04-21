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

def clean_text(text):

    cleaned = ""
    previous_space = False

    for char in text:

        if 'A' <= char <= 'Z':
            char = chr(ord(char) + 32)

        if char.isalnum() or char in [' ', '\n', '@', '.', '/', ':']:

            if char == " ":
                if not previous_space:
                    cleaned += char
                previous_space = True
            else:
                cleaned += char
                previous_space = False

    return cleaned

def tokenize(text):

    words = text.split()

    tokens = []

    for word in words:
        tokens.append(word)

    return tokens