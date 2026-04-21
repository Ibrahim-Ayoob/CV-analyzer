from analysis_logic import check_keywords, check_sections, calculate_score, generate_suggestions


cv_text = """
I am a frontend developer skilled in HTML, CSS and JavaScript.
I have experience working on web applications.
"""

keywords = ["HTML", "CSS", "JavaScript", "React", "Git"]

found_keywords, missing_keywords = check_keywords(cv_text, keywords)
found_sections, missing_sections = check_sections(cv_text)

score = calculate_score(found_keywords, len(keywords), found_sections)
suggestions = generate_suggestions(missing_keywords, missing_sections)

print("Found Keywords:", found_keywords)
print("Missing Keywords:", missing_keywords)
print("Missing Sections:", missing_sections)
print("Score:", score)
print("Suggestions:", suggestions)