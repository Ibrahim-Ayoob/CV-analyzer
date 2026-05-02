"""
analyzer.py — CV Analysis Module
----------------------------------
Applies rule-based evaluation to extracted CV text.
Produces a score (0–100) and a list of structured feedback items.

Each feedback item has the shape:
  { "type": "positive" | "warning" | "negative", "message": str }
"""

import re
from typing import TypedDict

# ---------------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------------

class FeedbackItem(TypedDict):
    type: str    # "positive", "warning", "negative"
    message: str


class AnalysisResult(TypedDict):
    score: int
    feedback: list[FeedbackItem]
    sections_found: int
    skills_count: int
    word_count: int
    breakdown: dict[str, int]


# ---------------------------------------------------------------------------
# Keywords & patterns
# ---------------------------------------------------------------------------

# Common CV section headers (case-insensitive)
SECTION_PATTERNS = {
    "Contact":       r"\b(contact|email|phone|linkedin|github|address)\b",
    "Summary":       r"\b(summary|objective|profile|about me|professional summary)\b",
    "Experience":    r"\b(experience|work experience|employment|work history|career)\b",
    "Education":     r"\b(education|academic|degree|university|college|school)\b",
    "Skills":        r"\b(skills|technical skills|competencies|technologies|tools)\b",
    "Projects":      r"\b(projects|personal projects|portfolio|side projects)\b",
    "Certifications": r"\b(certifications?|licenses?|credentials?|courses?)\b",
    "Languages":     r"\b(languages?|spoken languages?|fluency)\b",
}

# Technical & professional skills keywords
SKILL_KEYWORDS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "swift", "kotlin", "php", "r", "matlab", "scala",
    # Web
    "html", "css", "react", "angular", "vue", "node", "django", "flask",
    "fastapi", "spring", "laravel", "express",
    # Data / ML / AI
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
    "numpy", "scikit-learn", "nlp", "computer vision",
    # DevOps / Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "git",
    "ci/cd", "jenkins", "terraform", "ansible",
    # Soft skills
    "leadership", "communication", "teamwork", "problem solving",
    "project management", "agile", "scrum",
]

# Action verbs that signal strong, quantified experience
ACTION_VERBS = [
    "developed", "designed", "built", "implemented", "led", "managed",
    "created", "improved", "optimized", "launched", "deployed", "architected",
    "delivered", "achieved", "increased", "reduced", "automated",
]

# Quantification patterns (numbers + units)
QUANTIFICATION_RE = re.compile(
    r"\b\d+\s*(%|percent|users|clients|projects|employees|months|years|"
    r"hours|ms|seconds|k|m|million|billion)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(text: str) -> AnalysisResult:
    """
    Analyze extracted CV text and return a structured result.

    Args:
        text: Cleaned plain text from the CV.

    Returns:
        AnalysisResult dict with score, feedback, and metadata.
    """
    text_lower = text.lower()
    words      = text.split()
    word_count = len(words)

    feedback: list[FeedbackItem] = []
    score = 0

    # ── 1. Sections ────────────────────────────────────────────────────────
    found_sections: list[str] = []
    for section, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text_lower):
            found_sections.append(section)

    sections_found = len(found_sections)
    section_score  = min(sections_found * 5, 30)  # up to 30 pts
    score += section_score

    if "Experience" in found_sections:
        feedback.append({"type": "positive", "message": "Work experience section detected — great foundation for recruiters."})
    else:
        feedback.append({"type": "negative", "message": "No work experience section found. Add an 'Experience' section with your job history."})

    if "Education" in found_sections:
        feedback.append({"type": "positive", "message": "Education section is present."})
    else:
        feedback.append({"type": "negative", "message": "Education section is missing. Include your degrees and institutions."})

    if "Skills" in found_sections:
        feedback.append({"type": "positive", "message": "Skills section found — helps with ATS keyword matching."})
    else:
        feedback.append({"type": "warning", "message": "No dedicated Skills section. Consider adding one to improve ATS compatibility."})

    if "Summary" in found_sections:
        feedback.append({"type": "positive", "message": "Professional summary detected — strong opening for your CV."})
    else:
        feedback.append({"type": "warning", "message": "No summary or objective section. A brief 2–3 line summary can grab the recruiter's attention."})

    if "Contact" in found_sections:
        feedback.append({"type": "positive", "message": "Contact information is present."})
    else:
        feedback.append({"type": "negative", "message": "Contact information not detected. Make sure your email and phone number are clearly listed."})

    if "Projects" in found_sections:
        feedback.append({"type": "positive", "message": "Projects section found — demonstrates hands-on experience."})

    if "Certifications" in found_sections:
        feedback.append({"type": "positive", "message": "Certifications section detected — adds credibility."})

    # ── 2. Skills ──────────────────────────────────────────────────────────
    detected_skills = [kw for kw in SKILL_KEYWORDS if kw in text_lower]
    skills_count    = len(detected_skills)
    skill_score     = min(skills_count * 2, 25)  # up to 25 pts
    score += skill_score

    if skills_count >= 10:
        feedback.append({"type": "positive", "message": f"{skills_count} technical/professional skills detected — well-rounded skill set."})
    elif skills_count >= 5:
        feedback.append({"type": "warning", "message": f"Only {skills_count} skills detected. Consider expanding your skills section with relevant tools and technologies."})
    else:
        feedback.append({"type": "negative", "message": f"Very few skills detected ({skills_count}). Add more relevant technical and soft skills."})

    # ── 3. Quantification ──────────────────────────────────────────────────
    quant_matches = QUANTIFICATION_RE.findall(text)
    quant_count   = len(quant_matches)
    quant_score   = min(quant_count * 3, 15)  # up to 15 pts
    score += quant_score

    if quant_count >= 4:
        feedback.append({"type": "positive", "message": "Good use of quantified achievements (numbers/metrics detected). This strengthens credibility."})
    elif quant_count >= 1:
        feedback.append({"type": "warning", "message": "Some metrics found, but consider adding more quantified results (e.g., 'reduced load time by 40%')."})
    else:
        feedback.append({"type": "negative", "message": "No quantified achievements detected. Use numbers to demonstrate the impact of your work."})

    # ── 4. Action verbs ────────────────────────────────────────────────────
    action_count = sum(1 for v in ACTION_VERBS if v in text_lower)
    verb_score   = min(action_count * 1, 10)  # up to 10 pts
    score += verb_score

    if action_count >= 6:
        feedback.append({"type": "positive", "message": "Strong use of action verbs — your descriptions sound dynamic and results-driven."})
    elif action_count >= 2:
        feedback.append({"type": "warning", "message": "A few action verbs found. Use more active language (e.g., 'developed', 'led', 'optimized')."})
    else:
        feedback.append({"type": "negative", "message": "Action verbs are mostly absent. Start bullet points with power verbs to make achievements stand out."})

    # ── 5. Length / word count ─────────────────────────────────────────────
    length_score = 0
    if 300 <= word_count <= 900:
        length_score = 10
        feedback.append({"type": "positive", "message": f"CV length is ideal ({word_count} words) — concise yet informative."})
    elif word_count < 300:
        length_score = 3
        feedback.append({"type": "negative", "message": f"CV is very short ({word_count} words). Expand with more detail about your experience and skills."})
    else:
        length_score = 5
        feedback.append({"type": "warning", "message": f"CV is quite long ({word_count} words). Consider trimming to 1–2 pages for better readability."})
    score += length_score

    # ── 6. Contact completeness ─────────────────────────────────────────────
    contact_score = 0
    if re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text_lower):
        contact_score += 5
    else:
        feedback.append({"type": "negative", "message": "No email address found. Include a professional email."})

    if re.search(r"linkedin\.com/in/", text_lower):
        contact_score += 5
        feedback.append({"type": "positive", "message": "LinkedIn profile URL detected — great for professional visibility."})
    else:
        feedback.append({"type": "warning", "message": "No LinkedIn profile detected. Adding it can improve recruiter outreach."})

    if re.search(r"github\.com/", text_lower):
        feedback.append({"type": "positive", "message": "GitHub profile detected — great for showcasing code and projects."})

    score += contact_score
    score = min(score, 100)  # cap at 100

    breakdown = {
        "Sections": round((section_score / 30) * 100) if section_score is not None else 0,
        "Skills": round((skill_score / 25) * 100) if skill_score is not None else 0,
        "Metrics": round((quant_score / 15) * 100) if quant_score is not None else 0,
        "Verbs": round((verb_score / 10) * 100) if verb_score is not None else 0,
        "Length": round((length_score / 10) * 100) if length_score is not None else 0,
        "Contact": round((contact_score / 10) * 100) if contact_score is not None else 0,
    }

    return AnalysisResult(
        score=score,
        feedback=feedback,
        sections_found=sections_found,
        skills_count=skills_count,
        word_count=word_count,
        breakdown=breakdown,
    )
