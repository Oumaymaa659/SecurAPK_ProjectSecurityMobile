import os
import shutil
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

from analyseur import (
    decompiler_apk, lister_fichiers_java, analyser_fichier_java,
    compter_par_gravite, extraire_bibliotheques_sbom, verifier_vulnerabilites_sbom
)
from ia_analyzer import analyser_code_avec_ia
from native_analyzer import analyser_natives
from cvss_scoring import calculate_global_score   # <-- NOUVEAU

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== HITL Database ====================
DB_PATH = "hitl_feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT,
            finding_id TEXT,
            original_verdict TEXT,
            corrected_verdict TEXT,
            auditor_comment TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_feedback(scan_id, finding_id, original, corrected, comment):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO feedback (scan_id, finding_id, original_verdict, corrected_verdict, auditor_comment, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (scan_id, finding_id, original, corrected, comment, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_feedback_by_scan(scan_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM feedback WHERE scan_id = ?', (scan_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# Initialiser la base de données au démarrage
init_db()
# =====================================================

def generer_pdf(rapport_path, output_pdf):
    """Génère un PDF à partir du fichier rapport.json"""
    with open(rapport_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    story = []
    
    # Titre
    story.append(Paragraph("Rapport d'analyse de sécurité mobile - SecurAPK", title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Résumé
    story.append(Paragraph("Résumé des vulnérabilités", heading_style))
    summary = data.get("issues", [])
    compteur = {"critique":0, "majeur":0, "mineur":0}
    for v in summary:
        grav = v.get("gravite", "").lower()
        if grav in compteur:
            compteur[grav] += 1
    story.append(Paragraph(f"• Critiques : {compteur['critique']}", normal_style))
    story.append(Paragraph(f"• Majeures : {compteur['majeur']}", normal_style))
    story.append(Paragraph(f"• Mineures : {compteur['mineur']}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Tableau des vulnérabilités
    story.append(Paragraph("Détail des vulnérabilités", heading_style))
    if summary:
        table_data = [["Fichier", "Ligne", "Type", "Gravité", "Source"]]
        for v in summary[:30]:
            table_data.append([
                v.get("fichier", "?"),
                str(v.get("ligne", "?")),
                v.get("type", "?"),
                v.get("gravite", "?"),
                v.get("source", "statique")
            ])
        table = Table(table_data, colWidths=[4*cm, 1.5*cm, 4*cm, 2.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("Aucune vulnérabilité détectée.", normal_style))
    
    story.append(Spacer(1, 1*cm))
    
    # SBOM
    story.append(Paragraph("Composition des bibliothèques (SBOM)", heading_style))
    sbom = data.get("sbom", [])
    if sbom:
        sbom_data = [["Bibliothèque", "Version", "Licence", "Vulnérabilités"]]
        for lib in sbom:
            sbom_data.append([
                lib.get("library", "?"),
                lib.get("version", "inconnue"),
                lib.get("license", "?"),
                ", ".join(lib.get("vulnerabilities", [])) or "Aucune"
            ])
        table_sbom = Table(sbom_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 4*cm])
        table_sbom.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        story.append(table_sbom)
    else:
        story.append(Paragraph("Aucune bibliothèque tierce détectée.", normal_style))
    
    doc.build(story)

@app.route('/')
def index():
    return jsonify({"message": "SecurAPK API is running. Use POST /analyze with an APK file."})

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Fichier vide'}), 400
    if not file.filename.endswith('.apk'):
        return jsonify({'error': 'Le fichier doit être une APK'}), 400

    apk_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(apk_path)

    try:
        # 1. Décompilation
        dossier_java = decompiler_apk(apk_path)
        if not dossier_java:
            return jsonify({'error': 'Échec de la décompilation'}), 500

        # 2. Analyse statique (11 règles)
        fichiers_java = lister_fichiers_java(dossier_java)
        print(f"[INFO] Analyse statique de {len(fichiers_java)} fichiers Java...")
        tous_resultats = []
        for f in fichiers_java:
            tous_resultats.extend(analyser_fichier_java(f))

        # 3. Analyse IA
        print("\n=== Analyse par IA ===")
        fichiers_ia = set()
        for r in tous_resultats:
            if "chemin" in r:
                fichiers_ia.add(r["chemin"])
        if len(fichiers_ia) < 20:
            mots_sensibles = ["cipher", "messagedigest", "random", "keystore", "trustmanager", "native", "jni"]
            for f in fichiers_java:
                if len(fichiers_ia) >= 20:
                    break
                if f in fichiers_ia:
                    continue
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as fd:
                        contenu_lower = fd.read().lower()
                        if any(mot in contenu_lower for mot in mots_sensibles):
                            fichiers_ia.add(f)
                except:
                    pass
        fichiers_ia = list(fichiers_ia)[:20]
        print(f"[IA] {len(fichiers_ia)} fichiers à analyser")
        resultats_ia = []
        for idx, f in enumerate(fichiers_ia, 1):
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fd:
                    code = fd.read()
                if len(code) < 100 or len(code) > 50000:
                    continue
                print(f"[IA] Analyse {idx}/{len(fichiers_ia)} : {os.path.basename(f)}")
                nouvelles_vulns = analyser_code_avec_ia(code, os.path.basename(f))
                for v in nouvelles_vulns:
                    if "gravite" not in v:
                        continue
                    v.setdefault("fichier", os.path.basename(f))
                    v.setdefault("source", "ia")
                    resultats_ia.append(v)
            except Exception as e:
                print(f"[IA] Erreur sur {f}: {e}")
        tous_resultats.extend(resultats_ia)

        # 4. Analyse native
        print("\n=== Analyse native ===")
        resultats_natifs = analyser_natives(apk_path)
        tous_resultats.extend(resultats_natifs)

        # 5. SBOM
        biblios = extraire_bibliotheques_sbom(dossier_java)
        sbom = verifier_vulnerabilites_sbom(biblios)

        # 6. Nettoyage
        shutil.rmtree(dossier_java, ignore_errors=True)
        os.remove(apk_path)

        # 7. Générer un identifiant de scan (timestamp)
        scan_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # 8. Calculer le score global CVSS
        compteur = compter_par_gravite(tous_resultats)
        global_score = calculate_global_score(tous_resultats)

        # 9. Sauvegarder le rapport dans un fichier JSON avec l'ID
        rapport_filename = f"rapport_{scan_id}.json"
        with open(rapport_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "scan_id": scan_id,
                "issues": tous_resultats,
                "sbom": sbom,
                "summary": compteur,
                "global_score": global_score
            }, f, indent=2, ensure_ascii=False)
        # Conserver aussi un rapport.json pour la compatibilité
        shutil.copy(rapport_filename, "rapport.json")

        # 10. Résultat
        return jsonify({
            'scan_id': scan_id,
            'summary': compteur,
            'issues': tous_resultats,
            'sbom': sbom,
            'global_score': global_score   # <-- NOUVEAU
        })

    except Exception as e:
        print("Erreur serveur :", str(e))
        return jsonify({'error': f'Erreur interne : {str(e)}'}), 500

# ==================== HITL Endpoints ====================
@app.route('/feedback', methods=['POST'])
def add_feedback():
    data = request.json
    required = ['scan_id', 'finding_id', 'original_verdict', 'corrected_verdict']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    save_feedback(
        data['scan_id'],
        data['finding_id'],
        data['original_verdict'],
        data['corrected_verdict'],
        data.get('comment', '')
    )
    return jsonify({'status': 'ok'})

@app.route('/feedback/<scan_id>', methods=['GET'])
def get_feedback(scan_id):
    rows = get_feedback_by_scan(scan_id)
    feedback_list = []
    for row in rows:
        feedback_list.append({
            'id': row[0],
            'scan_id': row[1],
            'finding_id': row[2],
            'original_verdict': row[3],
            'corrected_verdict': row[4],
            'comment': row[5],
            'timestamp': row[6]
        })
    return jsonify(feedback_list)
# =======================================================

@app.route('/export/pdf', methods=['GET'])
def export_pdf():
    rapport_path = 'rapport.json'
    if not os.path.exists(rapport_path):
        return jsonify({'error': 'Aucun rapport disponible. Lancez d\'abord une analyse.'}), 404
    
    pdf_path = 'rapport_secuapk.pdf'
    try:
        generer_pdf(rapport_path, pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name='rapport_secuapk.pdf')
    except Exception as e:
        return jsonify({'error': f'Erreur génération PDF : {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)