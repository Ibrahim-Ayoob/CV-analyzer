def check_keywords(cv_text, keywords):
    found = []
    missing = []

    for word in keywords:
        if word.lower() in cv_text.lower():
            found.append(word)
        else:
            missing.append(word)

    return found, missing




def check_sections(cv_text):
    sections = ["education", "experience", "skills", "projects", "contact"]
    found = []
    missing = []

    for sec in sections:
        if sec in cv_text.lower():
            found.append(sec)
        else:
            missing.append(sec)

    return found, missing




def calculate_score(found_keywords, total_keywords, found_sections):
    keyword_score = (len(found_keywords) / total_keywords) * 50

    section_score = (len(found_sections) / 5) * 30

    formatting_score = 15 

    total_score = keyword_score + section_score + formatting_score

    return round(total_score, 2)




def generate_suggestions(missing_keywords, missing_sections):
    suggestions = []

    for skill in missing_keywords:
        suggestions.append(f"Add skill: {skill}")

    for sec in missing_sections:
        suggestions.append(f"Add section: {sec}")

    return suggestions


