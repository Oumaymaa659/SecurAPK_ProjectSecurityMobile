# mobsf_integration.py
import requests
import json
import time
import os

MOBSF_URL = "http://localhost:8000/api/v1"
API_KEY = "49f9b7a920caaa977ed3df6790678586a2da6a3ff8501b6c6ce8d09ce6247cd4"

SEVERITY_MAPPING = {
    "critical": "critique",
    "high": "majeur",
    "medium": "majeur",
    "low": "mineur",
    "info": "mineur",
    "warning": "mineur"
}

def upload_apk(apk_path):
    headers = {"Authorization": API_KEY}
    with open(apk_path, "rb") as f:
        files = {"file": (os.path.basename(apk_path), f, "application/vnd.android.package-archive")}
        resp = requests.post(f"{MOBSF_URL}/upload", files=files, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"Upload failed: {resp.text}")
    return resp.json().get("hash")

def wait_for_scan_completion(file_hash, max_wait=60):
    """Attend que le rapport soit disponible (scan statique automatique)."""
    headers = {"Authorization": API_KEY}
    start = time.time()
    while time.time() - start < max_wait:
        try:
            report_resp = requests.get(f"{MOBSF_URL}/report_json?hash={file_hash}", headers=headers, timeout=30)
            if report_resp.status_code == 200 and report_resp.text.strip():
                return True
        except:
            pass
        time.sleep(5)
    return False

def get_report(file_hash):
    headers = {"Authorization": API_KEY}
    resp = requests.get(f"{MOBSF_URL}/report_json?hash={file_hash}", headers=headers, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"Report failed: {resp.text}")
    return resp.json()

def convert_mobsf_finding_to_secuapk(finding):
    title = finding.get("title", "")
    description = finding.get("description", "")
    severity = finding.get("severity", "info").lower()
    gravite = SEVERITY_MAPPING.get(severity, "mineur")
    line = finding.get("line", 0)
    file_name = finding.get("file", "unknown.java")
    patch = "Consulter la documentation OWASP MASTG pour corriger cette vulnérabilité."
    return {
        "fichier": file_name,
        "chemin": file_name,
        "ligne": line,
        "type": title,
        "gravite": gravite,
        "explication": description,
        "patch": patch,
        "extrait": "",
        "source": "mobsf",
        "masvs": "MASVS-UNKNOWN"
    }

def analyser_avec_mobsf(apk_path):
    try:
        print("[MobSF] Upload de l'APK...")
        file_hash = upload_apk(apk_path)
        print(f"[MobSF] Hash: {file_hash}")
        print("[MobSF] Attente de la fin du scan statique...")
        if not wait_for_scan_completion(file_hash):
            print("[MobSF] Délai d'attente dépassé, tentative de récupération du rapport quand même...")
        print("[MobSF] Récupération du rapport...")
        report = get_report(file_hash)
        findings = report.get("findings", [])
        print(f"[MobSF] {len(findings)} vulnérabilités trouvées.")
        converted = [convert_mobsf_finding_to_secuapk(f) for f in findings]
        try:
            requests.delete(f"{MOBSF_URL}/delete", data={"hash": file_hash}, headers={"Authorization": API_KEY})
        except:
            pass
        return converted
    except Exception as e:
        print(f"[MobSF] Erreur : {e}")
        return []