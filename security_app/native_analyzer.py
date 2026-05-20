import os
import zipfile
import shutil
import subprocess
import json
import re

# Chemin absolu vers radare2 (à adapter si nécessaire)
R2_PATH = r"C:\radare2\radare2-6.1.4-w64\bin\r2.exe"

def extraire_libs_natives(apk_path, dossier_libs="libs_natives"):
    """Extrait tous les fichiers .so de l'APK."""
    if os.path.exists(dossier_libs):
        shutil.rmtree(dossier_libs)
    os.makedirs(dossier_libs)
    with zipfile.ZipFile(apk_path, 'r') as z:
        for info in z.infolist():
            if info.filename.endswith(".so"):
                target = os.path.join(dossier_libs, os.path.basename(info.filename))
                with open(target, 'wb') as out:
                    out.write(z.read(info.filename))
    return [os.path.join(dossier_libs, f) for f in os.listdir(dossier_libs) if f.endswith(".so")]

def detecter_chaine_dangereuse(chaine):
    """Détecte les chaînes liées à la crypto."""
    chaine_lower = chaine.lower()
    patterns = {
        "md5": "MD5",
        "sha1": "SHA1",
        "aes/ecb": "AES/ECB",
        "aes/cbc": "AES/CBC",
        "rand()": "rand() (aléatoire faible)",
        "srand": "srand() (aléatoire faible)",
        "random": "random() (aléatoire faible)",
        "openssl": "Utilisation d'OpenSSL (vérifier version)",
        "crypto": "Présence de crypto",
    }
    for key, label in patterns.items():
        if key in chaine_lower:
            return label
    return None

def est_cle_hex_longue(chaine):
    """Teste si la chaîne ressemble à une clé hexadécimale longue (>=32 caractères)."""
    if re.fullmatch(r'[0-9a-fA-F]{32,}', chaine):
        return True
    return False

def analyser_so_avec_r2(so_path):
    """Analyse un .so avec radare2 pour détecter des vulnérabilités cryptographiques."""
    resultats = []
    mots_dangereux = [
        "password", "secret", "key", "token", "api_key",
        "md5", "sha1", "aes", "ecb", "cbc", "gcm",
        "rand", "srand", "random", "crypto", "decrypt", "encrypt"
    ]
    fonctions_crypto = [
        "MD5_Init", "MD5_Update", "MD5_Final",
        "SHA1_Init", "SHA1_Update", "SHA1_Final",
        "EVP_CipherInit", "EVP_EncryptInit", "EVP_DecryptInit",
        "RAND_bytes", "RAND_pseudo_bytes",
        "DES_set_key", "AES_set_encrypt_key"
    ]
    
    try:
        import r2pipe
        r2 = r2pipe.open(R2_PATH)
        r2.cmd(f"o {so_path}")
        r2.cmd("aaa")  # analyse automatique
        
        # 1. Analyse des chaînes
        strings = r2.cmdj("izzj")
        for s in strings:
            chaine = s.get("string", "")
            chaine_lower = chaine.lower()
            # Vérifier les mots dangereux
            for mot in mots_dangereux:
                if mot in chaine_lower:
                    resultats.append({
                        "fichier": os.path.basename(so_path),
                        "type": f"Chaîne suspecte : {mot}",
                        "gravite": "majeur",
                        "explication": f"La bibliothèque native contient la chaîne '{chaine}' (indice de secret ou de fonction crypto).",
                        "patch": "Ne pas stocker de secrets en clair ; utiliser des API sécurisées et éviter les chaînes identifiables.",
                        "source": "native"
                    })
                    break
            # Détection spécifique de clé hexadécimale longue
            if est_cle_hex_longue(chaine):
                resultats.append({
                    "fichier": os.path.basename(so_path),
                    "type": "Clé hexadécimale codée en dur",
                    "gravite": "critique",
                    "explication": f"Une chaîne hexadécimale longue '{chaine[:20]}...' pourrait être une clé cryptographique.",
                    "patch": "Ne pas coder de clés en dur ; utiliser Android Keystore ou une gestion sécurisée des clés.",
                    "source": "native"
                })
        
        # 2. Analyse des imports (fonctions cryptographiques)
        imports = r2.cmdj("iij")  # imports JSON
        for imp in imports:
            nom = imp.get("name", "")
            for func in fonctions_crypto:
                if func.lower() in nom.lower():
                    resultats.append({
                        "fichier": os.path.basename(so_path),
                        "type": f"Fonction crypto détectée : {nom}",
                        "gravite": "majeur",
                        "explication": f"La bibliothèque importe la fonction '{nom}', utilisée pour des opérations cryptographiques. Vérifier son usage (algorithmes faibles, mauvais paramètres).",
                        "patch": "Utiliser des API modernes (libsodium, BoringSSL) et éviter les implémentations manuelles dangereuses.",
                        "source": "native"
                    })
                    break
        
        # 3. Fonctions JNI (Java_*)
        fonctions = r2.cmdj("aflj")
        jni_functions = [f.get("name") for f in fonctions if f.get("name", "").startswith("Java_")]
        if jni_functions:
            resultats.append({
                "fichier": os.path.basename(so_path),
                "type": f"Fonctions JNI ({len(jni_functions)})",
                "gravite": "majeur",
                "explication": "Les fonctions JNI peuvent exposer des vulnérabilités (buffer overflow, manipulation de données).",
                "patch": "Auditer chaque fonction JNI : validation des entrées, éviter les fonctions C dangereuses.",
                "source": "native"
            })
        
        r2.quit()
    except ImportError:
        # Fallback : utiliser la commande strings
        print(f"[NATIVE] r2pipe non disponible, analyse basique strings pour {so_path}")
        try:
            result = subprocess.run(f'strings "{so_path}"', shell=True, capture_output=True, text=True, timeout=30)
            contenu = result.stdout.lower()
            for mot in mots_dangereux:
                if mot in contenu:
                    resultats.append({
                        "fichier": os.path.basename(so_path),
                        "type": f"Chaîne suspecte : {mot}",
                        "gravite": "majeur",
                        "explication": f"La bibliothèque native contient la chaîne '{mot}' (analyse basique).",
                        "patch": "Vérifier manuellement la bibliothèque.",
                        "source": "native"
                    })
            # Détection de clés hexadécimales via regex
            hex_keys = re.findall(r'\b[0-9a-f]{32,}\b', result.stdout)
            for key in hex_keys[:5]:  # limiter l'affichage
                resultats.append({
                    "fichier": os.path.basename(so_path),
                    "type": "Clé hexadécimale codée en dur",
                    "gravite": "critique",
                    "explication": f"Clé hexadécimale potentielle : {key[:20]}...",
                    "patch": "Ne pas coder de clés en dur.",
                    "source": "native"
                })
        except Exception as e:
            print(f"[NATIVE] Erreur fallback : {e}")
    except Exception as e:
        print(f"[NATIVE] Erreur sur {so_path} : {e}")
    return resultats

def analyser_natives(apk_path):
    libs = extraire_libs_natives(apk_path)
    if not libs:
        print("[NATIVE] Aucune bibliothèque native trouvée.")
        return []
    print(f"[NATIVE] {len(libs)} bibliothèques natives extraites.")
    toutes_vulns = []
    for lib in libs:
        print(f"[NATIVE] Analyse de {os.path.basename(lib)}...")
        vulns = analyser_so_avec_r2(lib)
        toutes_vulns.extend(vulns)
    return toutes_vulns