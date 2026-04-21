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

def remove_stopwords(tokens):

    stopwords = [
        "the","and","is","a","to","in","of","for","on","with","at","by",
        "an","be","this","that","from","or","as","are"
    ]

    filtered = []

    for word in tokens:
        if word not in stopwords:
            filtered.append(word)

    return filtered

def word_frequency(tokens):

    freq = {}

    for word in tokens:

        if word in freq:
            freq[word] += 1
        else:
            freq[word] = 1

    return freq


def extract_emails(tokens):

    emails = []

    for word in tokens:

        if "@" in word and "." in word:
            emails.append(word)

    return emails


def extract_phones(tokens):

    phones = []

    for word in tokens:

        digits = ""

        for char in word:
            if char.isdigit():
                digits += char

        if len(digits) >= 10 and len(digits) <= 15:
            phones.append(digits)

    return phones