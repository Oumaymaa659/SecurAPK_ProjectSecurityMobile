# SecurAPK – Analyse statique de sécurité mobile

**SecurAPK** est un outil d’analyse statique conçu pour détecter les mauvaises pratiques cryptographiques dans les applications Android (fichiers APK). Il décompile l’APK avec `jadx`, inspecte le code Java généré à l’aide de 11 règles de détection (MD5, SHA1, AES/ECB, clés codées en dur, RNG faible, stockage non sécurisé, etc.) et fournit pour chaque vulnérabilité une explication du risque (risk reasoning) et un correctif type (patch). Une interface web réactive (React) permet de téléverser l’APK, de visualiser les résultats et d’exporter un rapport JSON.

---

## Fonctionnalités principales

- **Décompilation automatique** via `jadx` (option `--show-bad-code`)
- **11 règles de détection** couvrant :
  - MD5 / SHA1 (hachage faible)
  - AES/ECB et AES/CBC sans authentification
  - Clés statiques codées en dur
  - `java.util.Random` (RNG prévisible)
  - Stockage de clés dans `SharedPreferences` ou en fichier clair
  - TrustManager sans validation / HostnameVerifier `ALLOW_ALL`
  - IV fixe (mineur)
- **Classification** des vulnérabilités : `critique`, `majeur`, `mineur`
- **Risk reasoning** + **correctif type** pour chaque problème
- **SBOM (Software Bill of Materials)** basée sur les instructions `import` des fichiers Java (bibliothèques tierces)
- **Interface web** (React) avec upload d’APK, affichage des résultats et export JSON
- **Serveur backend** (Flask) orchestrant l’analyse

---

## Installation

### Prérequis

- Python 3.10 ou supérieur
- Node.js (pour le frontend React)
- Java Runtime Environment (JRE) pour `jadx`
- `jadx` (ligne de commande) téléchargeable depuis [jadx releases](https://github.com/skylot/jadx/releases)

### Cloner le dépôt

```bash
git clone https://github.com/Oumaymaa659/SecurAPK.git
cd SecurAPK
```
