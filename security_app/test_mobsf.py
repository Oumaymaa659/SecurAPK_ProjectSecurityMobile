import requests
import json

MOBSF_URL = "http://localhost:8000/api/v1"
API_KEY = "your_api_key"   # Tu trouveras la clé dans l'interface web : settings -> API Key

def upload_apk(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{MOBSF_URL}/upload", files=files, headers={"Authorization": API_KEY})
    return resp.json()["hash"]

def scan_apk(file_hash):
    resp = requests.post(f"{MOBSF_URL}/scan", data={"hash": file_hash}, headers={"Authorization": API_KEY})
    return resp.json()

# Exemple
hash = upload_apk("InsecureBankv2.apk")
results = scan_apk(hash)
print(json.dumps(results, indent=2))