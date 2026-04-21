from extractor import extract_text
import json

file_path = "MayaHashem_cv.pdf"

result = extract_text(file_path)

print(json.dumps(result, indent=4))