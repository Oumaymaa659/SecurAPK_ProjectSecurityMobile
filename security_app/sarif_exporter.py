# sarif_exporter.py
import json

def generate_sarif(issues, output_file="output.sarif"):
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