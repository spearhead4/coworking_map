import streamlit as st
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from streamlit_folium import st_folium

# --------------------
# CONFIGURATION
# --------------------
BASE_URL = "https://www.leportagesalarial.com/coworking/"
RAW_CSV = "coworking_info.csv"
CLEAN_CSV = "coworking_info_cleaned.csv"
# --------------------
# FONCTIONS UTILITAIRES
# --------------------

def extract_urls_from_first_ul(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        st.error(f"Erreur lors de la récupération des URLs: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    main_div = soup.find('div', class_='inner-post-entry')
    if not main_div:
        st.warning("Div principal non trouvé.")
        return []

    ul_elements = main_div.find_all('ul')
    if not ul_elements:
        st.warning("Aucun <ul> trouvé.")
        return []

    first_ul = ul_elements[0]
    links = []
    for link in first_ul.find_all('a', href=True):
        href = link['href']
        links.append(href if href.startswith('http') else base_url + href)

    return links

def extract_coworking_info(urls):
    coworking_data = []

    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            st.warning(f"Erreur en accédant à {url}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        info_div = soup.find('div', class_='inner-post-entry')
        if not info_div:
            continue

        info = {'URL': url}

        h2_tag = info_div.find('h2')
        if h2_tag:
            nom = h2_tag.text
            for prefix in ['Contacter ', 'Présentation de ', 'Présentation du ', 'Présentation : ']:
                nom = nom.replace(prefix, '')
            info['Nom'] = nom.strip()
        else:
            info['Nom'] = "indisponible"

        ul_element = info_div.find('ul')
        if ul_element:
            for li in ul_element.find_all('li'):
                text = li.get_text(strip=True)
                if "Adresse" in text:
                    info['Adresse'] = text.split(":", 1)[-1].strip()
                elif "Téléphone" in text:
                    info['Téléphone'] = text.split(":", 1)[-1].strip()
                elif "Site" in text:
                    link = li.find('a', href=True)
                    info['Site web'] = link['href'] if link else "indisponible"
                elif "Accès" in text:
                    info['Accès métro'] = text.split(":", 1)[-1].strip()

        for key in ['Adresse', 'Téléphone', 'Site web', 'Accès métro']:
            if key not in info:
                info[key] = "indisponible"

        coworking_data.append(info)

    return coworking_data

def normalize_text(text):
    if pd.isna(text):
        return text
    # Nettoyage Unicode
    text = unicodedata.normalize('NFKD', str(text))
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return text

def clean_data_file(input_path, output_path):
    # Lecture du CSV avec correction d'encodage
    df = pd.read_csv(input_path, encoding='utf-8')

    # Normalisation des colonnes mal encodées
    df.columns = [normalize_text(col) for col in df.columns]

    # Normalisation des valeurs texte
    for col in df.columns:
        df[col] = df[col].apply(normalize_text)

    # Suppression des lignes où URL, Nom ou Adresse sont NaN
    df = df.dropna(subset=["URL", "Nom", "Adresse"])

    # Suppression des lignes si URL, Nom ou Adresse valent "indisponible"
    required_cols = ["URL", "Nom", "Adresse"]
    cleaned_df = df.loc[
        (df[required_cols] != "indisponible").all(axis=1)
    ]

    # Sauvegarde
    cleaned_df.to_csv(output_path, index=False, encoding='utf-8')
    return cleaned_df

def geocode_addresses(df, address_column="Adresse"):
    geolocator = Nominatim(user_agent="coworking-map")
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1,         # Respecte 1 requête/s
        max_retries=3,               # Réessaie si ça échoue
        error_wait_seconds=2.0,      # Attente avant retry en cas d'erreur
        swallow_exceptions=False     # Laisse passer les erreurs critiques
    )

    # Initialise les colonnes
    if "Latitude" not in df.columns:
        df["Latitude"] = None
    if "Longitude" not in df.columns:
        df["Longitude"] = None

    for i, row in df.iterrows():
        # Skip si coordonnées déjà présentes
        if pd.notnull(row.get("Latitude")) and pd.notnull(row.get("Longitude")):
            continue

        try:
            location = geocode(row[address_column])
            if location:
                df.at[i, "Latitude"] = location.latitude
                df.at[i, "Longitude"] = location.longitude
            else:
                st.warning(f"Adresse non trouvée : {row[address_column]}")
        except Exception as e:
            st.error(f"Erreur géocodage à l’index {i} : {e}")

    return df


# --------------------
# INTERFACE STREAMLIT
# --------------------

st.title("📍 Coworkings en Île-de-France")

if st.button("🔍 Lancer le scraping"):
    with st.spinner("Extraction des liens..."):
        urls = extract_urls_from_first_ul(BASE_URL)

    if not urls:
        st.error("Aucun lien trouvé.")
    else:
        st.success(f"{len(urls)} liens trouvés.")
        with st.spinner("Scraping des informations..."):
            data = extract_coworking_info(urls)
            df = pd.DataFrame(data)
            df.to_csv(RAW_CSV, index=False, encoding='utf-8')
        st.success("✅ Scraping terminé.")
        st.dataframe(df)

if st.button("🧹 Nettoyer les données"):
    if not os.path.exists(RAW_CSV):
        st.error("Le fichier CSV brut est introuvable.")
    else:
        cleaned_df = clean_data_file(RAW_CSV, CLEAN_CSV)
        st.success("✅ Données nettoyées.")
        st.dataframe(cleaned_df)

if st.checkbox("📄 Voir le CSV brut"):
    if os.path.exists(RAW_CSV):
        df = pd.read_csv(RAW_CSV)
        st.dataframe(df)
    else:
        st.warning("Fichier non trouvé.")

if st.checkbox("📄 Voir le CSV nettoyé"):
    if os.path.exists(CLEAN_CSV):
        df = pd.read_csv(CLEAN_CSV)
        st.dataframe(df)
    else:
        st.warning("Fichier non trouvé.")

# --------------------
# BARRE DE RECHERCHE PERSISTANTE
# --------------------

st.subheader("🔎 Rechercher un coworking")

if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = pd.DataFrame()

search_term = st.text_input(
    "Entrez un mot-clé (nom, adresse, téléphone, etc.)",
    value="",
    help="La recherche s'effectue dans toutes les colonnes du fichier nettoyé."
)

if st.button("Rechercher"):
    if os.path.exists(CLEAN_CSV):
        df_search = pd.read_csv(CLEAN_CSV)

        mask = df_search.apply(
            lambda row: row.astype(str)
                           .str.contains(search_term, case=False, na=False)
                           .any(),
            axis=1
        )

        st.session_state.filtered_df = df_search[mask]
        st.session_state.filtered_df.to_csv("search.csv", index=False, encoding="utf-8")
        st.success(f"{len(st.session_state.filtered_df)} résultat(s) trouvé(s).")
    else:
        st.warning("Fichier nettoyé manquant. Veuillez lancer le nettoyage d'abord.")

# Affichage des résultats persistants
if not st.session_state.filtered_df.empty:
    st.dataframe(st.session_state.filtered_df)


# --------------------
# AFFICHAGE DE LA CARTE
# --------------------

df_map = None

# Charger les données nettoyées si elles existent
if os.path.exists(CLEAN_CSV):
    df_map = pd.read_csv(CLEAN_CSV)

    # Vérifie si les colonnes GPS existent
    has_coords = "Latitude" in df_map.columns and "Longitude" in df_map.columns
    if has_coords:
        df_map = df_map.dropna(subset=["Latitude", "Longitude"])

# Bouton pour rafraîchir les coordonnées (géocodage)
if st.button("🔄 Rafraîchir la carte (géolocaliser les adresses)"):
    if df_map is None or df_map.empty:
        st.error("❌ Les données nettoyées sont manquantes ou vides.")
    else:
        with st.spinner("📍 Géocodage des adresses..."):
            df_map = geocode_addresses(df_map)
            df_map.to_csv(CLEAN_CSV, index=False, encoding='utf-8')
        st.success("✅ Coordonnées mises à jour.")

# --------------------
# AFFICHER LA CARTE GÉNÉRALE
# --------------------

if st.checkbox("🗺️ Afficher la carte générale"):
    if os.path.exists(CLEAN_CSV):
        df_full_map = pd.read_csv(CLEAN_CSV)

        if "Latitude" in df_full_map.columns and "Longitude" in df_full_map.columns:
            df_full_map = df_full_map.dropna(subset=["Latitude", "Longitude"])

            if not df_full_map.empty:
                st.subheader("🗺️ Carte de tous les coworkings")
                m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)

                for _, row in df_full_map.iterrows():
                    folium.Marker(
                        location=[row["Latitude"], row["Longitude"]],
                        popup=row["Nom"],
                        tooltip=row["Nom"]
                    ).add_to(m)

                st_folium(m, width=700, height=500)
            else:
                st.info("Aucune donnée géolocalisée disponible.")
        else:
            st.warning("Colonnes 'Latitude' et 'Longitude' absentes dans le fichier nettoyé.")
    else:
        st.warning("Fichier 'coworking_info_cleaned.csv' introuvable.")


# --------------------
# AFFICHER LES RÉSULTATS DE RECHERCHE SUR LA CARTE
# --------------------

if st.checkbox("📍 Afficher la recherche sur la carte"):
    if os.path.exists("search.csv"):
        df_search_map = pd.read_csv("search.csv")
        if "Latitude" in df_search_map.columns and "Longitude" in df_search_map.columns:
            df_search_map = df_search_map.dropna(subset=["Latitude", "Longitude"])

            if not df_search_map.empty:
                st.subheader("🗺️ Carte des résultats filtrés")
                m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)

                for _, row in df_search_map.iterrows():
                    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
                        folium.Marker(
                            location=[row["Latitude"], row["Longitude"]],
                            popup=row["Nom"],
                            tooltip=row["Nom"]
                        ).add_to(m)

                st_folium(m, width=700, height=500)
            else:
                st.info("Aucune coordonnée disponible dans les résultats filtrés.")
        else:
            st.warning("Le fichier `search.csv` ne contient pas de coordonnées. Cliquez d'abord sur « Rafraîchir la carte ».")
    else:
        st.warning("Fichier `search.csv` introuvable. Effectuez d'abord une recherche.")
