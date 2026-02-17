import streamlit as st
import requests
import pandas as pd 
import plotly.express as px  # <--- CORRECTION 1 : import express

# 1. Configuration de la page (UNE SEULE FOIS AU DÉBUT)
st.set_page_config(page_title="MNS Occasions", layout="centered", page_icon="🚗")

# --- GESTION DE LA SESSION (LOGIN) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🔐 Connexion")
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            if username == "admin" and password == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

def logout():
    st.session_state.logged_in = False
    st.rerun()

# --- LOGIQUE D'AFFICHAGE ---
if not st.session_state.logged_in:
    login_page()
else:
    # Barre latérale
    st.sidebar.title("Menu")
    st.sidebar.write(f"Connecté en tant que : **admin**")
    if st.sidebar.button("Déconnexion"):
        logout()

    # Création des onglets
    tab1, tab2 = st.tabs(["🎯 Prédiction", "📈 Statistiques"])

    # --- ONGLET 1 : PRÉDICTION ---
    with tab1:
        st.title("🚗 MNS Occasions")
        st.write("Obtenez une estimation par IA en un clic.")

        with st.form("prediction_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                brand = st.text_input("Marque", value="Maruti")
                location = st.selectbox("Ville", ["Mumbai", "Hyderabad", "Kochi", "Coimbatore", "Delhi", "Kolkata", "Chennai", "Jaipur", "Bangalore", "Ahmedabad"])
                fuel = st.selectbox("Carburant", ["Petrol", "Diesel", "CNG", "LPG"])
            with col2:
                model_car = st.text_input("Modèle", value="Swift")
                year = st.number_input("Année", min_value=1990, max_value=2026, value=2018)
                transmission = st.selectbox("Boîte", ["Manual", "Automatic"])
            with col3:
                km = st.number_input("Kilométrage", min_value=0, value=50000)
                power = st.number_input("Puissance (bhp)", min_value=0.0, value=75.0)
                mileage = st.number_input("Consommation", min_value=0.0, value=20.0)

            owner = st.selectbox("Propriétaire", ["First", "Second", "Third", "Fourth & Above"])
            submit = st.form_submit_button("Estimer le prix")

        if submit:
            payload = {
                "Location": location, "Year": int(year), "Kilometers_Driven": int(km),
                "Fuel_Type": fuel, "Transmission": transmission, "Owner_Type": owner,
                "Mileage": float(mileage), "Power": float(power), 
                "Model": model_car.upper(), "Brand": brand.upper()
            }
            try:
                with st.spinner('Analyse IA...'):
                    response = requests.post("http://127.0.0.1:8000/predict", json=payload)
                    prediction = response.json().get('predicted_price')
                    st.success(f"### 💰 Prix estimé : {round(prediction * 929, 2)} €")
            except Exception as e:
                st.error("L'API FastAPI est éteinte (port 8000).")

    # --- ONGLET 2 : STATISTIQUES ---
    with tab2:
        st.title("📈 Analyse du Marché")
        
        # On charge les données
        try:
            data = pd.read_csv('data/train_clean.csv') # Attention au chemin (slash /)

            # Filtres graphiques (uniquement visibles dans cet onglet)
            marques = st.multiselect("Filtrer par marque", options=data['Brand'].unique(), default=data['Brand'].unique()[:5])
            df_filtre = data[data['Brand'].isin(marques)]

            # Graphique 1
            st.subheader("Relation Puissance vs Prix")
            fig = px.scatter(
                df_filtre, x="Power", y="Price", size="Price", 
                color="Fuel_Type", hover_name="Brand", size_max=40,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Graphique 2 (Evolution)
            st.subheader("Évolution des prix par Année")
            # Moyenne par année pour une courbe plus propre
            df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index()
            fig_line = px.line(df_evol, x="Year", y="Price", color="Brand", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

        except FileNotFoundError:
            st.error("Le fichier 'data/train_clean.csv' est introuvable.")