# Générer le README.md pour documenter le projet Streamlit
readme_content = """
# 🏢 Streamlit Coworking Scraper

Ce projet est une application Streamlit qui scrape automatiquement des espaces de coworking depuis le site [leportagesalarial.com](https://www.leportagesalarial.com/coworking/), nettoie les données, permet des recherches interactives, et affiche les résultats sur une carte interactive via Folium.

---

## 🚀 Fonctionnalités

- Scraping des liens de pages d'espaces de coworking
- Extraction des informations (nom, adresse, téléphone, accès métro, site web)
- Nettoyage et normalisation des données
- Recherche multi-champs (nom, adresse, site, etc.)
- Carte géographique des coworkings avec géocodage OpenStreetMap
- Affichage des résultats filtrés sur une carte séparée

---

## ⚙️ Installation

1. Cloner le projet

git clone <url-du-projet>
cd <nom-du-dossier>

2. Créer un environnement virtuel (Mac/Linux)

python3 -m venv env
source env/bin/activate

(Windows)

python -m venv env
env\\Scripts\\activate

3. Lancer l'application

streamlit run app.py
