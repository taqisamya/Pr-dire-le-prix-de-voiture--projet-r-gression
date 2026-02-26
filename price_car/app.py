
import streamlit as st
import requests
import pandas as pd 
import plotly.express as px
import sqlite3
import hashlib

# 1. Configuration de la page
st.set_page_config(page_title="MNS Occasions", layout="wide", page_icon="🚗")

# =============================
# DATABASE & DATA LOADING
# =============================
def create_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_db()

@st.cache_data
def load_car_data():
    try:
        df = pd.read_csv('data/train_clean.csv')
        # On s'assure que tout est en majuscule pour la cohérence
        df['Brand'] = df['Brand'].str.upper()
        df['Model'] = df['Model'].str.upper()
        return df
    except FileNotFoundError:
        return None

df_cars = load_car_data()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    data = cursor.fetchone()
    conn.close()
    return data

# =============================
# SESSION
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# =============================
# LOGIN PAGE
# =============================
def login_page():
    st.title("🔐 Connexion")
    menu = ["Connexion", "Inscription"]
    choice = st.radio("Choisissez une option", menu)
    if choice == "Connexion":
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    elif choice == "Inscription":
        new_user = st.text_input("Nouveau nom d'utilisateur")
        new_password = st.text_input("Nouveau mot de passe", type="password")
        if st.button("Créer un compte"):
            if add_user(new_user, new_password):
                st.success("Compte créé avec succès ✅")
            else:
                st.error("Utilisateur déjà existant.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# =============================
# LOGIQUE D'AFFICHAGE
# =============================
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("Menu")
    st.sidebar.write(f"Connecté : **{st.session_state.username}**")
    if st.sidebar.button("Déconnexion"):
        logout()

    tab1, tab2 = st.tabs(["🎯 Prédiction", "📈 Statistiques"])

    with tab1:
        st.title("🚗 MMS Occasions")
        st.write("Obtenez une estimation par IA basée sur les données du marché.")

        if df_cars is not None:
            with st.form("prediction_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Liste des marques uniques triées
                    list_brands = sorted(df_cars['Brand'].unique())
                    brand_selected = st.selectbox("Marque", list_brands)
                    
                    location = st.selectbox("Ville", ["Mumbai", "Hyderabad", "Kochi", "Coimbatore", "Delhi", "Kolkata", "Chennai", "Jaipur", "Bangalore", "Ahmedabad"])
                    fuel = st.selectbox("Carburant", ["Petrol", "Diesel", "CNG", "LPG"])
                
                with col2:
                    # Filtrage dynamique des modèles selon la marque choisie
                    models_filtered = sorted(df_cars[df_cars['Brand'] == brand_selected]['Model'].unique())
                    model_selected = st.selectbox("Modèle", models_filtered)
                    
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
                    "Location": location,
                    "Year": int(year),
                    "Kilometers_Driven": int(km),
                    "Fuel_Type": fuel,
                    "Transmission": transmission,
                    "Owner_Type": owner,
                    "Mileage": float(mileage),
                    "Power": float(power),
                    "Model": model_selected,
                    "Brand": brand_selected
                }

                try:
                    with st.spinner('Analyse IA...'):
                        response = requests.post("http://127.0.0.1:8000/predict", json=payload)
                        prediction = response.json().get('predicted_price')

                        if prediction is not None:
                            # Conversion approximative (selon votre coefficient 929)
                            prix_euros = round(prediction * 929, 2)
                            st.success(f"### 💰 Prix estimé : {prix_euros} €")
                        else:
                            st.error("Erreur dans la réponse API.")
                except Exception:
                    st.error("L'API FastAPI est éteinte (port 8000).")
        else:
            st.error("Impossible de charger les données pour les listes déroulantes.")

    # with tab2:
    #     st.title("📈 Analyse du Marché")
    #     if df_cars is not None:
    #         marques = st.multiselect(
    #             "Filtrer par marque",
    #             options=df_cars['Brand'].unique(),
    #             default=df_cars['Brand'].unique()[:5]
    #         )

    #         df_filtre = df_cars[df_cars['Brand'].isin(marques)]

    #         st.subheader("Relation Puissance vs Prix")
    #         fig = px.scatter(
    #             df_filtre, x="Power", y="Price", size="Price",
    #             color="Fuel_Type", hover_name="Model", size_max=40, template="plotly_dark"
    #         )
    #         st.plotly_chart(fig, use_container_width=True)

    #         st.subheader("Évolution des prix par Année")
    #         df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index()
    #         fig_line = px.line(df_evol, x="Year", y="Price", color="Brand", markers=True)
    #         st.plotly_chart(fig_line, use_container_width=True)
    #     else:
    #         st.error("Le fichier 'data/train_clean.csv' est introuvable.")



    with tab2:
        st.title("📈 Analyse du Marché")
        try:
            # Utilisation de os.path pour éviter les erreurs de slash selon Windows/Linux
            import os
            path = os.path.join('data', 'train_clean.csv')
            data = pd.read_csv(path)

            # 1. Filtre par marque
            marques = st.multiselect(
                "Filtrer par marque", 
                options=sorted(data['Brand'].unique()), # Trié par ordre alphabétique c'est mieux !
                placeholder="Choisir une (ou plusieurs) marque(s)"
            )

            # 2. Sécurité : On ne trace que si une marque est sélectionnée
            if marques:
                df_filtre = data[data['Brand'].isin(marques)]

                # --- Graphique 1 : Histogramme ---
                st.subheader("Distribution des Prix par Type de Carburant")
                fig = px.histogram(
                    df_filtre, 
                    x="Fuel_Type", 
                    y="Price", 
                    color="Fuel_Type",
                    histfunc="avg", 
                    template="plotly_dark",
                    barmode="group",
                    labels={"Fuel_Type": "Type de Carburant", "Price": "Prix Moyen (en €)"}
                )
                fig.update_layout(bargap=0.2)
                st.plotly_chart(fig, use_container_width=True)

                # --- Graphique 2 : Courbe d'évolution ---
                st.subheader("Évolution des prix (en €) par Année")
                # Tri par année pour que la ligne ne s'entremêle pas
                df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index().sort_values('Year')
                
                fig_line = px.line(
                    df_evol, 
                    x="Year", 
                    y="Price", 
                    color="Brand", 
                    markers=True,
                    template="plotly_dark", # Pour rester cohérent avec le thème dark
                    labels={"Year": "Année", "Price": "Prix Moyen (€)"}
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            else:
                # Message d'accueil si rien n'est sélectionné
                st.info("💡 Veuillez sélectionner au moins une marque pour afficher les statistiques du marché.")

        except FileNotFoundError:
            st.error("❌ Le fichier 'train_clean.csv' est introuvable dans le dossier 'data'.")
        except Exception as e:
            st.error(f"⚠️ Une erreur est survenue : {e}")