const mockData = {
  summary: { critical: 2, major: 5, minor: 3 },
  crypto_issues: [
    {
      id: 1,
      file: "MainActivity.java",
      line: 42,
      type: "AES_no_auth",
      severity: "critique",
      risk_explanation:
        "L'utilisation d'AES en mode ECB ne fournit aucune authentification des données chiffrées. Un attaquant peut modifier les blocs chiffrés sans que l'application ne détecte la falsification, ce qui peut mener à des attaques par oracle de padding ou à l'injection de données malveillantes.",
      code_snippet: 'Cipher.getInstance("AES/ECB/PKCS5Padding")',
      recommended_patch: 'Cipher.getInstance("AES/GCM/NoPadding")',
    },
    {
      id: 2,
      file: "CryptoHelper.java",
      line: 18,
      type: "WEAK_HASH",
      severity: "critique",
      risk_explanation:
        "L'utilisation de MD5 pour le hachage des mots de passe est extrêmement vulnérable aux attaques par force brute et aux tables arc-en-ciel. MD5 est considéré comme cryptographiquement cassé depuis 2004.",
      code_snippet: 'MessageDigest.getInstance("MD5")',
      recommended_patch: 'MessageDigest.getInstance("SHA-256")',
    },
    {
      id: 3,
      file: "NetworkManager.java",
      line: 87,
      type: "SSL_NO_VERIFY",
      severity: "majeur",
      risk_explanation:
        "La désactivation de la vérification des certificats SSL permet des attaques Man-in-the-Middle (MITM). Toutes les communications réseau peuvent être interceptées.",
      code_snippet: "TrustAllCertificates()",
      recommended_patch: "Utiliser le TrustManager par défaut du système",
    },
    {
      id: 4,
      file: "StorageUtils.java",
      line: 33,
      type: "HARDCODED_KEY",
      severity: "majeur",
      risk_explanation:
        "Une clé de chiffrement codée en dur dans le code source est facilement extractible par rétro-ingénierie de l'APK.",
      code_snippet: 'private static final String KEY = "MyS3cr3tK3y!"',
      recommended_patch:
        "Utiliser Android Keystore pour stocker les clés de manière sécurisée",
    },
    {
      id: 5,
      file: "AuthService.java",
      line: 112,
      type: "INSECURE_RANDOM",
      severity: "majeur",
      risk_explanation:
        "java.util.Random n'est pas cryptographiquement sécurisé. Les tokens générés sont prévisibles.",
      code_snippet: "new Random().nextInt()",
      recommended_patch: "new SecureRandom().nextInt()",
    },
    {
      id: 6,
      file: "LoginActivity.java",
      line: 56,
      type: "LOG_SENSITIVE",
      severity: "majeur",
      risk_explanation:
        "Les informations sensibles logguées sont accessibles via ADB logcat sur des appareils rootés.",
      code_snippet: 'Log.d("AUTH", "password=" + password)',
      recommended_patch: "Supprimer les logs contenant des données sensibles",
    },
    {
      id: 7,
      file: "DatabaseHelper.java",
      line: 29,
      type: "SQL_INJECTION",
      severity: "majeur",
      risk_explanation:
        "La concaténation de chaînes pour construire des requêtes SQL permet l'injection SQL.",
      code_snippet: 'db.rawQuery("SELECT * FROM users WHERE id=" + userId)',
      recommended_patch:
        'db.rawQuery("SELECT * FROM users WHERE id=?", new String[]{userId})',
    },
    {
      id: 8,
      file: "FileUtils.java",
      line: 71,
      type: "WORLD_READABLE",
      severity: "mineur",
      risk_explanation:
        "Les fichiers accessibles en lecture par toutes les applications peuvent exposer des données sensibles.",
      code_snippet: "MODE_WORLD_READABLE",
      recommended_patch: "MODE_PRIVATE",
    },
    {
      id: 9,
      file: "WebViewActivity.java",
      line: 15,
      type: "JS_INTERFACE",
      severity: "mineur",
      risk_explanation:
        "L'interface JavaScript dans un WebView peut être exploitée pour exécuter du code arbitraire si le contenu web n'est pas de confiance.",
      code_snippet: 'webView.addJavascriptInterface(obj, "Android")',
      recommended_patch:
        "Utiliser @JavascriptInterface et valider le contenu chargé",
    },
    {
      id: 10,
      file: "DebugConfig.java",
      line: 8,
      type: "DEBUG_ENABLED",
      severity: "mineur",
      risk_explanation:
        "Le mode debug activé en production permet l'inspection détaillée de l'application.",
      code_snippet: "android:debuggable=\"true\"",
      recommended_patch: "android:debuggable=\"false\"",
    },
  ],
  sbom: [
    {
      library: "com.google.gson:gson",
      version: "2.8.6",
      license: "Apache-2.0",
      vulnerabilities: ["CVE-2022-25647"],
    },
    {
      library: "com.squareup.okhttp3:okhttp",
      version: "4.9.0",
      license: "Apache-2.0",
      vulnerabilities: [],
    },
    {
      library: "org.bouncycastle:bcprov-jdk15on",
      version: "1.65",
      license: "MIT",
      vulnerabilities: ["CVE-2020-28052", "CVE-2020-15522"],
    },
    {
      library: "com.squareup.retrofit2:retrofit",
      version: "2.9.0",
      license: "Apache-2.0",
      vulnerabilities: [],
    },
    {
      library: "androidx.sqlite:sqlite",
      version: "2.1.0",
      license: "Apache-2.0",
      vulnerabilities: ["CVE-2021-20223"],
    },
  ],
};

export default mockData;
