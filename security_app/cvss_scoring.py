# cvss_scoring.py
from cvss import CVSS3
import json

# Mapping sévérité SecurAPK → vecteur CVSS approximatif
SEVERITY_TO_CVSS_VECTOR = {
    "critique": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
    "majeur": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
    "mineur": "CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:L/I:L/A:L"
}

def calculate_cvss_score(severity: str) -> float:
    """Retourne le score CVSS (0-10) pour une sévérité donnée."""
    vector = SEVERITY_TO_CVSS_VECTOR.get(severity.lower(), SEVERITY_TO_CVSS_VECTOR["majeur"])
    try:
        cvss_obj = CVSS3(vector)
        return cvss_obj.scores()[0]  # score numérique
    except:
        return 5.0  # valeur par défaut

def calculate_global_score(issues: list) -> dict:
    """
    Calcule le score global de sécurité (0-100) et la note A-F.
    issues : liste de dictionnaires contenant au moins 'gravite'
    """
    if not issues:
        return {"score": 100, "grade": "A", "raw": 100}
    
    total_cvss = 0
    for issue in issues:
        severite = issue.get("gravite", "majeur")
        cvss = calculate_cvss_score(severite)
        total_cvss += cvss
    
    # Score maximal possible = 10 * nombre de vulnérabilités
    max_possible = 10 * len(issues)
    if max_possible == 0:
        raw_score = 100
    else:
        raw_score = max(0, 100 - (total_cvss / max_possible) * 100)
    
    # Conversion en note A-F
    if raw_score >= 90:
        grade = "A"
    elif raw_score >= 80:
        grade = "B"
    elif raw_score >= 70:
        grade = "C"
    elif raw_score >= 60:
        grade = "D"
    elif raw_score >= 50:
        grade = "E"
    else:
        grade = "F"
    
    return {"score": round(raw_score, 1), "grade": grade, "raw": raw_score}