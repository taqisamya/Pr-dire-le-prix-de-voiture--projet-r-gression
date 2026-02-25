import streamlit as st
import requests
import pandas as pd 
import plotly.express as px 
import sqlite3
import base64

df = pd.read_csv("data\\train_clean.csv")

st.set_page_config(page_title="MMS Occasions", layout="centered", page_icon="🚗")


def check_login(username, password):
    """Vérifie si le couple user/password existe en base de données."""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM profils WHERE user = ? AND password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None 
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données : {e}")
        return False

def login_page():
    st.title("🔐 Connexion")
    
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")
        
        if submit:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Utilisateur ou mot de passe incorrect.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False

if not st.session_state.logged_in:
    if not st.session_state.show_login:
        # --- PAGE D'ACCUEIL ---
        st.title("🚗 Bienvenue chez MMS Occasions")
        st.write("<div style='text-align: center'>L'outil expert pour estimer la valeur de votre véhicule d'occasion en quelques secondes.</div>", unsafe_allow_html=True)
        st.markdown("\n\n")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            if st.button("Se connecter", type="primary"):
                st.session_state.show_login = True
                st.rerun()
        
        st.divider()
        st.info("Connectez-vous pour accéder aux prédictions IA et aux statistiques du marché.")
    else:
        # --- PAGE DE LOGIN ---
        login_page()
        if st.button("Retour"):
            st.session_state.show_login = False
            st.rerun()

else:
    # --- APPLICATION APRÈS CONNEXION ---
    st.sidebar.success(f"Vous êtes connecté ! ")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.show_login = False 
        st.rerun()

    tab1, tab2 = st.tabs(["🚦 Prédiction", "📈 Statistiques"])

    with tab1:
        st.title("🚗 MMS Occasions")
        st.write("Obtenez une estimation par IA en un clic.")

        marques_disponibles = sorted(df['Brand'].unique().tolist())

        st.subheader("Informations du véhicule")

        col_a, col_b = st.columns(2)

        with col_a:
            brand = st.selectbox("Marque", options=marques_disponibles)

        modeles_filtres = sorted(df[df['Brand'] == brand]['Model'].unique().tolist())

        with col_b:
            model_car = st.selectbox("Modèle", options=modeles_filtres)

        with st.form("prediction_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                owner = st.selectbox("Propriétaire", ["Première main", "Seconde main", "Troisième main", "Quatrième main ou plus"])
                if owner == "Première main":
                    owner = "First"
                elif owner =="Seconde main":
                    owner = "Second"
                elif owner == "Troisième main":
                    owner = "Third"
                elif owner == "Quatrième main ou plus":
                    owner = "Fourth & Above"
                fuel = st.selectbox("Carburant", ["Essence", "Diesel", "CNG", "LPG"])
                if fuel == "Essence":
                    fuel = "Petrol"
                
            with col2:
                year = st.number_input("Année", min_value=1998, max_value=2019, value=2010)
                transmission = st.selectbox("Boîte", ["Manuelle", "Automatique"])
                if transmission == "Manuelle":
                    transmission = "Manual"
                elif transmission == "Automatique":
                    transmission = "Automatic"
                
            with col3:
                km = st.number_input("Kilométrage", min_value=0, value=10000)
                power = st.number_input("Puissance (bhp)", min_value=0.0, value=50.0)

            mileage = st.number_input("Consommation (en kmpl)", min_value=0.0, value=20.0)
            location = st.selectbox("Ville", ["Mumbai", "Hyderabad", "Kochi", "Coimbatore", "Delhi", "Kolkata", "Chennai", "Jaipur", "Bangalore", "Ahmedabad"])
           
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

    with tab2:
        st.title("📈 Analyse du Marché")
        
        try:
            data = pd.read_csv('data\\train_clean.csv')

            marques = st.multiselect("Filtrer par marque", options=data['Brand'].unique(), placeholder="Choisir une (ou plusieurs) marque(s)")
            df_filtre = data[data['Brand'].isin(marques)]
            df_filtre["Price"] = df_filtre["Price"]*929

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


            st.subheader("Évolution des prix par Année")
            df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index()
            
            fig_line = px.line(df_evol, x="Year", y="Price", color="Brand", markers=True, labels={"Year":"Année", "Price":"Prix (en €)"})
            st.plotly_chart(fig_line, use_container_width=True)

        except FileNotFoundError:
            st.error("Le fichier 'data\\train_clean.csv' est introuvable.")