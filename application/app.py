import streamlit as st
import requests
import pandas as pd 
import plotly.express as px 
import sqlite3
import hashlib

df = pd.read_csv("data\\train_clean.csv")

st.set_page_config(page_title="MMS Occasions", layout="centered", page_icon="🚗")


def check_login(username, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        query = "SELECT password FROM profils WHERE user = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        
        conn.close()
        if result:
            return check_password_hash(password, result[0])
        return False 
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données : {e}")
        return False
    
def create_account(username, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT user FROM profils WHERE user = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Cet utilisateur existe déjà."

        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO profils (user, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True, "Compte créé avec succès !"
    except sqlite3.Error as e:
        return False, f"Erreur : {e}"

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

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password_hash(password, hashed_password):
    return hash_password(password) == hashed_password



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False

if not st.session_state.logged_in:
    if not st.session_state.show_login:
        # --- PAGE D'ACCUEIL ---
        st.title("🚗 Bienvenue chez MMS Occasions")
        st.image('background.png')
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
        choice = st.radio("Actions", ["Se connecter", "Créer un compte"], horizontal=True)

        if choice == "Se connecter":
            login_page()
        else:
            st.title("📝 Créer un compte")
            with st.form("signup_form"):
                new_user = st.text_input("Choisir un nom d'utilisateur")
                new_pw = st.text_input("Choisir un mot de passe", type="password")
                confirm_pw = st.text_input("Confirmer le mot de passe", type="password")
                submit_signup = st.form_submit_button("S'inscrire")

                if submit_signup:
                    if new_pw != confirm_pw:
                        st.error("Les mots de passe ne correspondent pas.")
                    elif len(new_pw) < 3:
                        st.error("Le mot de passe est trop court.")
                    else:
                        success, message = create_account(new_user, new_pw)
                        if success:
                            st.success(message)
                            st.info("Vous pouvez maintenant vous connecter.")
                        else:
                            st.error(message)

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
                fuel = st.selectbox("Carburant", ["Essence", "Diesel", "Gaz naturel comprimé", "Gaz propane liquéfié"])
                if fuel == "Essence":
                    fuel = "Petrol"
                elif fuel == 'Gaz naturel comprimé':
                    fuel = 'CNG'
                elif fuel == 'Gaz propane liquéfié':
                    fuel = 'LPG'
                
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
                    # response = requests.post("http://127.0.0.1:8000/prediction", json=payload)
                    response = requests.post("http://127.0.0.1:8000/prediction", params=payload)
                    prediction = response.json().get('predicted_price')
                    st.success(f"""### 💰 Prix estimé : {round(prediction * 929, 2)} €\n 💰 Prix non converti : {round(prediction, 2)} Lakhs""")
            except Exception as e:
                st.error("L'API FastAPI est éteinte (port 8000).")

    with tab2:
        st.title("📈 Analyse du Marché")
        
        try:
            data = pd.read_csv('data\\train_clean.csv')

            marques = st.multiselect("Filtrer par marque", options=data['Brand'].unique(), default=data['Brand'].unique(),placeholder="Choisir une (ou plusieurs) marque(s)")
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