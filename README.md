# CV Analyzer — Phase 1

A web-based CV analysis system. Upload a PDF resume and receive a score + structured feedback.

---

## Project Structure

```
cv-analyzer/
├── frontend/
│   ├── index.html       ← React frontend entry point
│   └── CVAnalyzer.jsx   ← React UI component + upload logic
├── app.py               ← Flask server (Backend)
├── extractor.py         ← PDF text extraction module
├── analyzer.py          ← Rule-based CV analysis module
├── requirements.txt     ← Python dependencies
└── README.md            ← Project documentation
```

---

## Team Responsibilities

| Member | Role | Files |
|--------|------|-------|
| Member 1 | Frontend Developer | `react` |
| Member 2 | Backend Developer | `app.py` |
| Member 3 | Text Extraction | `extractor.py` |
| Member 4 | Analysis | `analyzer.py` |

---

## Setup & Run

### 1. Backend + Frontend

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

Open the app at: **http://127.0.0.1:5000**

The Flask server now serves the static frontend from the `frontend/` folder and exposes the upload API at `/upload`.

---

---

## API Reference

### `POST /upload`

Upload a CV file for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (PDF, max 10MB)

**Response (200):**
```json
{
  "score": 72,
  "sections_found": 5,
  "skills_count": 11,
  "word_count": 480,
  "feedback": [
    { "type": "positive", "message": "Work experience section detected." },
    { "type": "warning",  "message": "No LinkedIn profile detected." },
    { "type": "negative", "message": "No quantified achievements found." }
  ]
}
```

**Error response:**
```json
{ "error": "Only PDF files are accepted." }
```

---

## Scoring Breakdown

| Category | Max Points |
|----------|-----------|
| Sections present (×5 each) | 30 |
| Skills detected (×2 each) | 25 |
| Quantified achievements (×3 each) | 15 |
| Action verbs (×1 each) | 10 |
| CV length (ideal: 300–900 words) | 10 |
| Contact completeness | 10 |
| **Total** | **100** |

---

## Development Workflow

- Each team member works on their own Git branch
- Use Pull Requests to merge into `main`
- Use GitHub Issues for task tracking

### Suggested branches:
```
feature/frontend
feature/backend
feature/extractor
feature/analyzer
```

---

## Notes

- This is a **Phase 1 demo** using simplified rule-based logic.
- Uploaded files are deleted after processing — not stored permanently.
- Phase 2 improvements may include ML-based analysis, more detailed feedback, and user accounts.
