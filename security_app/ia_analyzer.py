import requests
import json
import hashlib
import os
import re
import sqlite3

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:7b"

CACHE_FILE = "ia_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def extraire_json_depuis_texte(texte):
    """Extrait un objet JSON valide à partir d'une chaîne bavarde."""
    texte = re.sub(r'```json\s*', '', texte)
    texte = re.sub(r'```\s*$', '', texte)
    debut = texte.find('{')
    fin = texte.rfind('}')
    if debut != -1 and fin != -1 and debut < fin:
        candidate = texte[debut:fin+1]
        try:
            json.loads(candidate)
            return candidate
        except:
            pass
    match = re.search(r'\{[^{}]*"findings"\s*:\s*\[.*?\]\}', texte, re.DOTALL)
    if match:
        return match.group(0)
    return "{}"

def get_few_shot_examples(limit=3):
    """Récupère les 'limit' derniers feedbacks HITL (TP/FP) pour servir d'exemples."""
    db_path = "hitl_feedback.db"
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Récupère les dernières corrections (les plus récentes d'abord)
    c.execute("""
        SELECT original_verdict, corrected_verdict, auditor_comment
        FROM feedback
        WHERE corrected_verdict IN ('TP', 'FP')
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    examples = []
    for original, corrected, comment in rows:
        examples.append({
            "original_verdict": original,
            "corrected_verdict": corrected,
            "comment": comment
        })
    return examples

def analyser_code_avec_ia(code: str, filename: str) -> list:
    code = code[:2000]
    code_hash = hashlib.md5(code.encode()).hexdigest()
    cache = load_cache()
    if code_hash in cache:
        return cache[code_hash]

    # Construction du contexte few‑shot
    few_shot_examples = get_few_shot_examples(3)
    few_shot_text = ""
    if few_shot_examples:
        few_shot_text = "\nVoici des exemples de corrections effectuées par des experts sur des vulnérabilités similaires (feedback HITL) :\n"
        for ex in few_shot_examples:
            few_shot_text += f"- Verdict original: {ex['original_verdict']} → corrigé en {ex['corrected_verdict']} (commentaire: {ex['comment']})\n"
        few_shot_text += "Utilise ces exemples pour affiner ton propre jugement.\n"

    prompt = f"""
Ton rôle : Tu es un expert en sécurité des applications mobiles (OWASP MASVS). Tu analyses un fichier Java extrait d'une application Android pour trouver des vulnérabilités de sécurité.

{few_shot_text}

Instructions :
- Tu ne retournes **que** un objet JSON valide. Aucun autre texte.
- Si tu trouves des vulnérabilités, utilise le format suivant :
    "findings": [
        {{
            "type": "type de vulnérabilité",
            "severity": "critique|majeur|mineur",
            "line": numéro_de_ligne (si possible, sinon 0),
            "explanation": "description claire du risque",
            "patch": "code corrigé"
        }}
    ]
- Si tu ne trouves AUCUNE vulnérabilité, retourne exactement : {{"findings": []}}

Vulnérabilités à rechercher (liste non exhaustive) :
- Injections (SQL, commandes système)
- Mauvaises pratiques crypto (MD5, SHA1, clés en dur, modes faibles, IV fixes)
- Fuites d'informations (mots de passe, tokens, logs)
- Failles de logique métier (contournement d'authentification, élévation de privilèges)
- Fichiers vulnérables (export de composants, WebViews)

Fichier : {filename}
Code :
{code}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                }
            },
            timeout=300
        )
        raw = response.json().get("response", "")
        json_text = extraire_json_depuis_texte(raw)
        data = json.loads(json_text)
        findings = data.get("findings", [])
        valid_findings = []
        for f in findings:
            if not isinstance(f, dict):
                continue
            if "severity" in f and "gravite" not in f:
                f["gravite"] = f.pop("severity")
            if "gravite" not in f or "type" not in f:
                continue
            if f["gravite"].lower() not in ["critique", "majeur", "mineur"]:
                f["gravite"] = "majeur"
            f["fichier"] = filename
            f["source"] = "ia"
            f.setdefault("line", 0)
            f.setdefault("explication", "Vulnérabilité détectée par IA.")
            f.setdefault("patch", "Revoir le code selon les bonnes pratiques.")
            valid_findings.append(f)
        cache[code_hash] = valid_findings
        save_cache(cache)
        return valid_findings
    except Exception as e:
        print(f"[IA] Erreur lors de l'appel à Ollama : {e}")
        return []