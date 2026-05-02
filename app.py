"""
app.py — Flask Backend Server
------------------------------
Manages file upload, orchestrates extraction and analysis,
and returns a structured JSON response to the frontend.

Run:
    pip install flask flask-cors pymupdf
    python app.py
"""

import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from extractor import extract_text
from analyzer  import analyze

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__, static_folder="frontend", static_url_path="")

# Allow requests from the frontend (served from any origin in dev)
CORS(app)

# Folder where uploaded CVs are saved temporarily
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE_MB   = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    """Return True if the file has a .pdf extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def safe_filename(original: str) -> str:
    """Generate a unique safe filename to avoid collisions or path traversal."""
    ext = original.rsplit(".", 1)[-1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Serve the frontend application."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "CV Analyzer backend is running"}), 200


@app.route("/upload", methods=["POST"])
def upload():
    """
    POST /upload
    ------------
    Accepts a PDF file, runs extraction + analysis, returns JSON.

    Expected form-data:
        file: <PDF file>

    Returns JSON:
        {
          "score": int,
          "feedback": [{"type": str, "message": str}, ...],
          "sections_found": int,
          "skills_count": int,
          "word_count": int
        }

    Error response:
        { "error": str }
    """

    # ── Validate file presence ────────────────────────────────────────────
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]

    if file.filename == "" or file.filename is None:
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are accepted."}), 415

    # ── Validate file size ────────────────────────────────────────────────
    file.seek(0, 2)  # seek to end
    size_bytes = file.tell()
    file.seek(0)     # reset to start
    if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        return jsonify({"error": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit."}), 413

    # ── Save file ─────────────────────────────────────────────────────────
    saved_name = safe_filename(file.filename)
    save_path  = os.path.join(UPLOAD_FOLDER, saved_name)

    try:
        file.save(save_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    # ── Extract text ──────────────────────────────────────────────────────
    try:
        text = extract_text(save_path)
    except ValueError as e:
        _cleanup(save_path)
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        _cleanup(save_path)
        return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500

    # ── Analyze ───────────────────────────────────────────────────────────
    try:
        result = analyze(text)
    except Exception as e:
        _cleanup(save_path)
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    # ── Cleanup & respond ─────────────────────────────────────────────────
    _cleanup(save_path)
    return jsonify(result), 200


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cleanup(path: str) -> None:
    """Silently delete a file after processing."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass  # non-critical — log in production


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("  CV Analyzer Backend — Phase 1")
    print("  Running on http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="127.0.0.1", port=5000)
