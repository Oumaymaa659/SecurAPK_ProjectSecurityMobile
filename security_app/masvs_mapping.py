# masvs_mapping.py
# Correspondance entre les types de vulnérabilités SecurAPK et les contrôles OWASP MASVS v2
# Référence : https://mas.owasp.org/MASVS/

MASVS_MAP = {
    # Hachages faibles
    "MD5": "MASVS-CRYPTO-1",
    "SHA1": "MASVS-CRYPTO-1",
    
    # Modes de chiffrement non authentifiés
    "AES_ECB": "MASVS-CRYPTO-2",
    "AES_CBC_sans_auth": "MASVS-CRYPTO-2",
    
    # Clés statiques / codées en dur
    "Cle_statique_dure": "MASVS-CRYPTO-3",
    
    # RNG faible
    "Random_java_util": "MASVS-CRYPTO-3",
    
    # Stockage non sécurisé des clés
    "Stockage_cle_SharedPreferences": "MASVS-STORAGE-1",
    "Cle_fichier_clair": "MASVS-STORAGE-1",
    
    # TLS / réseau
    "TrustManager_insecure": "MASVS-NETWORK-2",
    "HostnameVerifier_all": "MASVS-NETWORK-2",
    
    # IV fixe
    "IV_fixe": "MASVS-CRYPTO-2",
}

def get_masvs_control(issue_type: str) -> str:
    """
    Retourne l'identifiant du contrôle MASVS v2 pour un type de vulnérabilité donné.
    Si non trouvé, retourne 'MASVS-UNKNOWN'.
    """
    return MASVS_MAP.get(issue_type, "MASVS-UNKNOWN")


# Optionnel : fonction pour obtenir la description courte d'un contrôle
MASVS_DESCRIPTIONS = {
    "MASVS-CRYPTO-1": "L'application utilise des primitives cryptographiques modernes et sécurisées.",
    "MASVS-CRYPTO-2": "L'application implémente correctement les mécanismes cryptographiques.",
    "MASVS-CRYPTO-3": "Les clés cryptographiques sont gérées de manière sécurisée (stockage, génération, rotation).",
    "MASVS-STORAGE-1": "Les données sensibles ne sont pas stockées en clair sur l'appareil.",
    "MASVS-NETWORK-2": "Les communications réseau sont sécurisées et valident correctement les certificats.",
}

def get_masvs_description(control: str) -> str:
    return MASVS_DESCRIPTIONS.get(control, "Contrôle MASVS non documenté.")