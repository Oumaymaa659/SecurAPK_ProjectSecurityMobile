import os
import subprocess
import re
import json
import shutil
import sys
import traceback

# === AJOUTS ===
from ia_analyzer import analyser_code_avec_ia
from native_analyzer import analyser_natives
from masvs_mapping import get_masvs_control
from mobsf_integration import analyser_avec_mobsf   # <-- NOUVEAU

# Chemin vers jadx.bat
JADX_PATH = r"C:\jadx\bin\jadx.bat"

def decompiler_apk(chemin_apk, dossier_sortie_java="decompiled_java"):
    if os.path.exists(dossier_sortie_java):
        shutil.rmtree(dossier_sortie_java)
    commande = f'"{JADX_PATH}" --show-bad-code -d {dossier_sortie_java} "{chemin_apk}"'
    print("Commande exécutée :", commande)
    result = subprocess.run(commande, shell=True, capture_output=True, text=True)
    print("Code retour :", result.returncode)
    if result.stdout:
        print("STDOUT (début) :", result.stdout[:500])
    if result.stderr:
        print("STDERR (début) :", result.stderr[:500])
    if result.returncode != 0:
        if os.path.exists(dossier_sortie_java) and any(os.scandir(dossier_sortie_java)):
            print("Attention : jadx a rencontré des erreurs mais a produit des fichiers.")
            return dossier_sortie_java
        else:
            print("Erreur jadx : aucun fichier produit.")
            return None
    return dossier_sortie_java

def lister_fichiers_java(dossier):
    fichiers = []
    for racine, _, noms in os.walk(dossier):
        for nom in noms:
            if nom.endswith(".java"):
                fichiers.append(os.path.join(racine, nom))
    return fichiers

# ======================== RÈGLES CRYPTO ========================
REGLES_CRYPTO = [
    {
        "nom": "MD5",
        "pattern": r'MessageDigest\.getInstance\s*\(\s*"MD5"\s*\)',
        "gravite": "majeur",
        "explication": "MD5 est un hachage cassé. Utiliser SHA-256.",
        "patch": "MessageDigest.getInstance(\"SHA-256\")"
    },
    {
        "nom": "SHA1",
        "pattern": r'MessageDigest\.getInstance\s*\(\s*"SHA-?1"\s*\)',
        "gravite": "majeur",
        "explication": "SHA1 n'est plus sûr. Utiliser SHA-256.",
        "patch": "MessageDigest.getInstance(\"SHA-256\")"
    },
    {
        "nom": "AES_ECB",
        "pattern": r'Cipher\.getInstance\s*\(\s*"AES/ECB',
        "gravite": "critique",
        "explication": "Le mode ECB ne cache pas les répétitions. Préférer AES/GCM.",
        "patch": "Cipher.getInstance(\"AES/GCM/NoPadding\")"
    },
    {
        "nom": "AES_CBC_sans_auth",
        "pattern": r'Cipher\.getInstance\s*\(\s*"AES/CBC',
        "gravite": "majeur",
        "explication": "CBC sans intégrité permet des modifications du texte chiffré.",
        "patch": "Utiliser AES/GCM ou ajouter HMAC."
    },
    {
        "nom": "Cle_statique_dure",
        "pattern": r'(secret\s*=\s*"?[A-Za-z0-9+/]{16,}")|(key\s*=\s*"?[0-9a-fA-F]{32,}")',
        "gravite": "critique",
        "explication": "Clé cryptographique codée en dur dans le code.",
        "patch": "Stocker la clé dans Android Keystore."
    },
    {
        "nom": "Random_java_util",
        "pattern": r'new\s+java\.util\.Random\s*\(',
        "gravite": "critique",
        "explication": "java.util.Random est prévisible pour la cryptographie.",
        "patch": "Utiliser java.security.SecureRandom"
    },
    {
        "nom": "Stockage_cle_SharedPreferences",
        "pattern": r'SharedPreferences\s*\.\s*edit\s*\(\s*\)\s*\.\s*putString\s*\(\s*["\'].*key.*["\']',
        "gravite": "critique",
        "explication": "Une clé cryptographique stockée dans les SharedPreferences n'est pas protégée.",
        "patch": "Utiliser Android Keystore pour générer et stocker les clés."
    },
    {
        "nom": "TrustManager_insecure",
        "pattern": r'TrustManager.*\{\s*public\s+void\s+checkServerTrusted.*\{\s*\}',
        "gravite": "critique",
        "explication": "TrustManager sans validation réelle expose aux attaques MITM.",
        "patch": "Ne pas désactiver la validation. Utiliser le TrustManager par défaut."
    },
    {
        "nom": "HostnameVerifier_all",
        "pattern": r'HOSTNAME_VERIFIER\s*=\s*ALLOW_ALL_HOSTNAME_VERIFIER',
        "gravite": "critique",
        "explication": "HostnameVerifier accepte tous les hôtes, annulant la vérification du certificat.",
        "patch": "Utiliser le vérificateur par défaut."
    },
    {
        "nom": "IV_fixe",
        "pattern": r'IvParameterSpec\s*\(\s*new\s+byte\s*\[\s*\]\s*\{[^}]*\}\s*\)\s*;?\s*//?\s*fixe',
        "gravite": "mineur",
        "explication": "IV fixe rend le chiffrement déterministe.",
        "patch": "Générer un IV aléatoire avec SecureRandom."
    },
    {
        "nom": "Cle_fichier_clair",
        "pattern": r'FileOutputStream.*\.write\s*\(.*key.*\)',
        "gravite": "critique",
        "explication": "Clé écrite en clair dans un fichier.",
        "patch": "Stocker la clé dans Android Keystore."
    },
]

def analyser_fichier_java(chemin_fichier):
    with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
        contenu = f.read()
    resultats = []
    for regle in REGLES_CRYPTO:
        for match in re.finditer(regle["pattern"], contenu, re.IGNORECASE):
            ligne = contenu[:match.start()].count('\n') + 1
            resultats.append({
                "fichier": os.path.basename(chemin_fichier),
                "chemin": chemin_fichier,
                "ligne": ligne,
                "type": regle["nom"],
                "gravite": regle["gravite"],
                "explication": regle["explication"],
                "patch": regle["patch"],
                "extrait": match.group().strip(),
                "source": "statique",
                "masvs": get_masvs_control(regle["nom"])
            })
    return resultats

def compter_par_gravite(resultats):
    compteur = {"critique": 0, "majeur": 0, "mineur": 0}
    for r in resultats:
        if "gravite" in r:
            grav = r["gravite"].lower()
            if grav in compteur:
                compteur[grav] += 1
        else:
            print(f"[ATTENTION] Résultat sans gravité ignoré : {r}")
    return compteur

# ======================== SBOM & vulnérabilités ========================
def extraire_bibliotheques_sbom(dossier_java):
    pattern_import = re.compile(r'^import\s+([a-zA-Z0-9_\.]+);', re.MULTILINE)
    system_prefixes = ('java.', 'javax.', 'android.', 'androidx.', 'com.android.',
                       'dalvik.', 'org.apache.harmony.', 'kotlin.', 'sun.', 'org.junit')
    libs = set()
    for fichier in lister_fichiers_java(dossier_java):
        with open(fichier, 'r', encoding='utf-8', errors='ignore') as f:
            contenu = f.read()
            for match in pattern_import.finditer(contenu):
                pkg = match.group(1)
                if any(pkg.startswith(p) for p in system_prefixes):
                    continue
                parts = pkg.split('.')
                if len(parts) >= 2:
                    libs.add(f"{parts[0]}.{parts[1]}")
    return list(libs)

def verifier_vulnerabilites_sbom(libs):
    fake_db = {
        "com.google.gson":     {"version": "2.8.6",   "license": "Apache-2.0", "vulns": ["CVE-2022-25647"]},
        "com.squareup.okhttp3":{"version": "4.9.0",   "license": "Apache-2.0", "vulns": []},
        "org.bouncycastle":    {"version": "1.65",    "license": "MIT",        "vulns": ["CVE-2020-28052"]},
        "com.squareup.retrofit2":{"version":"2.9.0",  "license": "Apache-2.0", "vulns": []},
        "androidx.sqlite":     {"version": "2.1.0",   "license": "Apache-2.0", "vulns": ["CVE-2021-20223"]},
    }
    resultats = []
    for lib in libs:
        info = fake_db.get(lib, {})
        resultats.append({
            "library": lib,
            "version": info.get("version", "inconnue"),
            "license": info.get("license", "À vérifier"),
            "vulnerabilities": info.get("vulns", [])
        })
    return resultats

def sauvegarder_rapport(resultats, sbom, nom_rapport="rapport.json"):
    with open(nom_rapport, 'w', encoding='utf-8') as f:
        json.dump({
            "issues": resultats,
            "sbom": sbom
        }, f, indent=2, ensure_ascii=False)
    print(f"Rapport sauvegardé dans {nom_rapport}")

# ======================== MAIN ========================
if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("Usage : python analyseur.py chemin_vers_apk")
            sys.exit(1)
        apk_path = sys.argv[1]
        if not os.path.exists(apk_path):
            print(f"Fichier introuvable : {apk_path}")
            sys.exit(1)

        print("\n=== ÉTAPE 1 : Décompilation de l'APK ===")
        dossier_java = decompiler_apk(apk_path)
        if dossier_java is None:
            print("Erreur de décompilation, arrêt.")
            sys.exit(1)

        print("\n=== ÉTAPE 2 : Analyse statique (11 règles) ===")
        fichiers_java = lister_fichiers_java(dossier_java)
        print(f"Fichiers Java trouvés : {len(fichiers_java)}")
        tous_resultats = []
        for f in fichiers_java:
            tous_resultats.extend(analyser_fichier_java(f))

        # === ÉTAPE 3 : Analyse IA optimisée ===
        print("\n=== ÉTAPE 3 : Analyse par IA (phi3:mini) ===")
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
        print(f"[IA] {len(fichiers_ia)} fichiers à analyser (parmi {len(fichiers_java)})")
        resultats_ia = []
        for idx, f in enumerate(fichiers_ia, 1):
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fd:
                    code = fd.read()
                if len(code) < 100 or len(code) > 50000:
                    if len(code) > 50000:
                        print(f"[IA] Fichier trop gros ({len(code)} octets), ignoré : {os.path.basename(f)}")
                    continue
                print(f"[IA] Analyse {idx}/{len(fichiers_ia)} : {os.path.basename(f)}")
                nouvelles_vulns = analyser_code_avec_ia(code, os.path.basename(f))
                for v in nouvelles_vulns:
                    if "gravite" not in v:
                        print(f"[IA] Vulnérabilité mal formée ignorée : {v}")
                        continue
                    v.setdefault("fichier", os.path.basename(f))
                    v.setdefault("source", "ia")
                    v.setdefault("masvs", get_masvs_control(v.get("type", "")))
                    resultats_ia.append(v)
            except Exception as e:
                print(f"[IA] Erreur sur fichier {f} : {e}")
                continue
        print(f"[IA] Terminé : {len(resultats_ia)} vulnérabilités trouvées par IA.")
        tous_resultats.extend(resultats_ia)

        # === ÉTAPE 4 : Analyse native (C++ / .so) ===
        print("\n=== ÉTAPE 4 : Analyse du code natif (C++/.so) ===")
        resultats_natifs = analyser_natives(apk_path)
        for v in resultats_natifs:
            v.setdefault("masvs", get_masvs_control(v.get("type", "")))
        tous_resultats.extend(resultats_natifs)

        # === ÉTAPE 5 : Extraction SBOM ===
        print("\n=== ÉTAPE 5 : Extraction SBOM ===")
        biblios = extraire_bibliotheques_sbom(dossier_java)
        sbom = verifier_vulnerabilites_sbom(biblios)


                # === ÉTAPE 6 : Analyse avec MobSF ===
        print("\n=== ÉTAPE 6 : Analyse avec MobSF ===")
        # resultats_mobsf = analyser_avec_mobsf(apk_path)
        resultats_mobsf = []  # désactivé
        tous_resultats.extend(resultats_mobsf)


        # === ÉTAPE 7 : Sauvegarde du rapport ===
        print("\n=== ÉTAPE 7 : Sauvegarde du rapport ===")
        sauvegarder_rapport(tous_resultats, sbom)

        compteur = compter_par_gravite(tous_resultats)
        print("\n--- RÉSUMÉ GLOBAL (statique + IA + native + MobSF) ---")
        print(f"Critiques : {compteur['critique']} | Majeurs : {compteur['majeur']} | Mineurs : {compteur['mineur']}")
        if tous_resultats:
            print("Aperçu des problèmes :")
            for r in tous_resultats[:10]:
                src = r.get("source", "inconnue")
                grav = r.get("gravite", "inconnue")
                typ = r.get("type", "inconnue")
                fich = r.get("fichier", "?")
                ligne = r.get("ligne", "?")
                masvs = r.get("masvs", "???")
                print(f"[{grav.upper()}] {typ} ({src}) - MASVS:{masvs} dans {fich} ligne {ligne}")
        else:
            print("Aucune vulnérabilité détectée.")
        print(f"\nBibliothèques détectées : {len(biblios)}")
        for b in sbom:
            print(f" - {b['library']} (vulns: {b['vulnerabilities']})")

    except Exception as e:
        print("\n=== ERREUR GLOBALE NON GÉRÉE ===")
        traceback.print_exc()
        sys.exit(1)