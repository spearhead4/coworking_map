# 🏢 Streamlit Coworking Scraper

Une application Streamlit complète pour :
- Scraper les espaces de coworking d’Île-de-France à partir du site [leportagesalarial.com](https://www.leportagesalarial.com/coworking/)
- Nettoyer et normaliser les données
- Rechercher un coworking par mot-clé
- Visualiser les adresses géolocalisées sur une carte interactive

---

## 🚀 Fonctionnalités

- 🔍 **Scraping automatique** des données (Nom, Adresse, Téléphone, Site Web, Accès métro)
- 🧹 **Nettoyage** des caractères spéciaux (`√©` → `é`) et suppression des données incomplètes
- 🔎 **Recherche multi-colonnes** sur toutes les informations
- 🗺️ **Carte Folium** interactive avec géocodage OpenStreetMap
- 📍 **Affichage géographique** des résultats filtrés

---

## ⚙️ Installation locale

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd <nom-du-dossier>
```
2. Créer un environnement virtuel
Sous macOS / Linux :

Toujours afficher les détails
```bash
python3 -m venv env
source env/bin/activate
```
Sous Windows :

Toujours afficher les détails
```bash
python -m venv env
env\\Scripts\\activate
```
3. Installer les dépendances

Toujours afficher les détails
```bash
pip install -r requirements.txt
```
📦 requirements.txt

Toujours afficher les détails

streamlit>=1.34
pandas>=2.2
requests>=2.31
beautifulsoup4>=4.12
geopy>=2.4
folium>=0.15
streamlit-folium>=0.14

▶️ Lancer l'application

Toujours afficher les détails
```bash
streamlit run app.py
```
🧭 Interface utilisateur
🔍 Lancer le scraping

    Récupère les liens de pages coworking, puis extrait les infos détaillées de chaque fiche.

🧹 Nettoyer les données

    Nettoie les accents mal encodés

    Supprime les lignes où l’URL, le Nom ou l’Adresse sont manquants ou "indisponible"

📄 Voir les CSV

    Affiche les fichiers CSV bruts et nettoyés.

🔎 Rechercher un coworking

    Permet de filtrer les résultats selon n’importe quel champ (Nom, Adresse, Téléphone, etc.)

🔄 Rafraîchir la carte

    Géocode les adresses manquantes avec Nominatim (1 requête/sec)

    Ajoute les coordonnées GPS dans le fichier nettoyé

🗺️ Afficher la carte générale

    Affiche tous les coworkings géolocalisés

📍 Afficher la recherche sur la carte

    Affiche uniquement les résultats filtrés sur une carte Folium

🛠 Remarques techniques

    Le géocodage utilise OpenStreetMap (Nominatim), limité à 1 requête/seconde.

    Sur macOS, en cas d'erreur SSL :

Toujours afficher les détails

/Applications/Python\\ 3.x/Install\\ Certificates.command

Ou bien :

Toujours afficher les détails

import os, certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

📁 Fichiers générés

    coworking_info.csv : données brutes scrappées

    coworking_info_cleaned.csv : données nettoyées et géocodées

    search.csv : résultats filtrés par la recherche utilisateur

✨ Auteur

Projet Streamlit conçu pour la visualisation intelligente de lieux de coworking à partir de données web publiques.