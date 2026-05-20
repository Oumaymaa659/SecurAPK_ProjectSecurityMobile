#!/usr/bin/env python3
# cli.py
import requests
import argparse
import sys
import json
from datetime import datetime

API_URL = "http://localhost:5000"

def generate_sarif(issues, output_file="output.sarif"):
    """Génère un fichier SARIF à partir des vulnérabilités."""
    sarif = {
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "SecurAPK", "version": "1.0"}},
            "results": []
        }]
    }
    for issue in issues:
        sarif["runs"][0]["results"].append({
            "ruleId": issue.get("type", "unknown"),
            "level": "error" if issue.get("gravite") == "critique" else "warning",
            "message": {"text": issue.get("explication", "")},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": issue.get("fichier", "unknown")},
                    "region": {"startLine": issue.get("ligne", 1)}
                }
            }]
        })
    with open(output_file, "w") as f:
        json.dump(sarif, f, indent=2)
    print(f"📄 Rapport SARIF généré : {output_file}")

def scan_apk(apk_path, fail_on, output_sarif=None):
    print(f"[SecurAPK] Upload de {apk_path}...")
    with open(apk_path, "rb") as f:
        files = {"file": f}
        try:
            resp = requests.post(f"{API_URL}/analyze", files=files)
        except requests.exceptions.ConnectionError:
            print("❌ Erreur : Impossible de joindre le backend. Vérifie que 'python app.py' est lancé.")
            return 1
    
    if resp.status_code != 200:
        print(f"❌ Erreur : {resp.json().get('error', 'Unknown error')}")
        return 1
    
    data = resp.json()
    scan_id = data.get("scan_id")
    global_score = data.get("global_score", {})
    score = global_score.get("score", 0)
    grade = global_score.get("grade", "?")
    summary = data.get("summary", {})
    issues = data.get("issues", [])
    
    print(f"\n✅ Analyse terminée (ID: {scan_id})")
    print(f"📊 Résumé : {summary.get('critique',0)} critiques, {summary.get('majeur',0)} majeures, {summary.get('mineur',0)} mineures")
    print(f"🎯 Score global : {score}/100 (Grade {grade})")
    
    # Génération SARIF si demandée
    if output_sarif:
        generate_sarif(issues, output_sarif)
    
    # Seuil de blocage
    if score < fail_on:
        print(f"❌ Échec du pipeline : score {score} < seuil {fail_on}")
        return 1
    else:
        print(f"✅ Seuil atteint : score {score} >= {fail_on}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="SecurAPK CLI - Analyse de sécurité mobile")
    parser.add_argument("apk", help="Chemin vers le fichier APK")
    parser.add_argument("--fail-on", type=int, default=70, help="Seuil d'échec (score < seuil = échec, défaut: 70)")
    parser.add_argument("--sarif", help="Générer un rapport SARIF (chemin du fichier de sortie)")
    args = parser.parse_args()
    
    sys.exit(scan_apk(args.apk, args.fail_on, args.sarif))

if __name__ == "__main__":
    main()