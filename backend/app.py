from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 🔹 Import modules (IMPORTANT: match your folder names)
from extractor.extractor import *
from analysis.analysis_logic import *

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==============================
# 🏠 HOME
# ==============================
@app.route("/")
def home():
    return "CV Analyzer Backend is Running 🚀"


# ==============================
# 📤 UPLOAD ROUTE
# ==============================
@app.route("/upload", methods=["POST"])
def upload_file():

    # 1. Validate request
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # 2. Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # ==============================
        # 📄 STEP 1: EXTRACT TEXT
        # ==============================
        extraction_result = extract_text(filepath)

        # 🔹 depends on your extraction output
        cv_text = extraction_result.get("clean_text", "")

        # ==============================
        # 🧠 STEP 2: ANALYSIS
        # ==============================
        keywords = [
            "python", "java", "sql", "machine learning",
            "ai", "flask", "django", "api", "github"
        ]

        found_keywords, missing_keywords = check_keywords(cv_text, keywords)
        found_sections, missing_sections = check_sections(cv_text)

        score = calculate_score(
            found_keywords,
            len(keywords),
            found_sections
        )

        suggestions = generate_suggestions(
            missing_keywords,
            missing_sections
        )

        # ==============================
        # 📤 STEP 3: RESPONSE
        # ==============================
        return jsonify({
            "score": score,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "found_sections": found_sections,
            "missing_sections": missing_sections,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# ▶️ RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)