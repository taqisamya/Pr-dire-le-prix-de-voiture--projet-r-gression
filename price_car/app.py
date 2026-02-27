
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
        
        # st.divider()
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

# import streamlit as st
# import requests
# import pandas as pd 
# import plotly.express as px
# import sqlite3
# import hashlib

# # 1. Configuration de la page
# st.set_page_config(page_title="MNS Occasions", layout="wide", page_icon="🚗")

# # =============================
# # DATABASE & DATA LOADING
# # =============================
# def create_db():
#     conn = sqlite3.connect("users.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL
#         )
# #     """)
# #     conn.commit()
# #     conn.close()

# # create_db()

# # @st.cache_data
# # def load_car_data():
# #     try:
# #         df = pd.read_csv('data/train_clean.csv')
# #         # On s'assure que tout est en majuscule pour la cohérence
# #         df['Brand'] = df['Brand'].str.upper()
# #         df['Model'] = df['Model'].str.upper()
# #         return df
# #     except FileNotFoundError:
# #         return None

# # df_cars = load_car_data()

# # def hash_password(password):
# #     return hashlib.sha256(password.encode()).hexdigest()

# # def add_user(username, password):
# #     conn = sqlite3.connect("users.db")
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
# #         conn.commit()
# #         return True
# #     except:
# #         return False
# #     finally:
# #         conn.close()

# # def login_user(username, password):
# #     conn = sqlite3.connect("users.db")
# #     cursor = conn.cursor()
# #     cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
# #     data = cursor.fetchone()
# #     conn.close()
# #     return data

# # # =============================
# # # SESSION
# # # =============================
# # if "logged_in" not in st.session_state:
# #     st.session_state.logged_in = False
# # if "username" not in st.session_state:
# #     st.session_state.username = ""

# # # =============================
# # # LOGIN PAGE
# # # =============================
# # def login_page():
# #     st.title("🔐 Connexion")
# #     menu = ["Connexion", "Inscription"]
# #     choice = st.radio("Choisissez une option", menu)
# #     if choice == "Connexion":
# #         username = st.text_input("Nom d'utilisateur")
# #         password = st.text_input("Mot de passe", type="password")
# #         if st.button("Se connecter"):
# #             user = login_user(username, password)
# #             if user:
# #                 st.session_state.logged_in = True
# #                 st.session_state.username = username
# #                 st.rerun()
# #             else:
# #                 st.error("Identifiants incorrects.")
# #     elif choice == "Inscription":
# #         new_user = st.text_input("Nouveau nom d'utilisateur")
# #         new_password = st.text_input("Nouveau mot de passe", type="password")
# #         if st.button("Créer un compte"):
# #             if add_user(new_user, new_password):
# #                 st.success("Compte créé avec succès ✅")
# #             else:
# #                 st.error("Utilisateur déjà existant.")

# # def logout():
# #     st.session_state.logged_in = False
# #     st.session_state.username = ""
# #     st.rerun()

# # # =============================
# # # LOGIQUE D'AFFICHAGE
# # # =============================
# # if not st.session_state.logged_in:
# #     login_page()
# # else:
# #     st.sidebar.title("Menu")
# #     st.sidebar.write(f"Connecté : **{st.session_state.username}**")
# #     if st.sidebar.button("Déconnexion"):
# #         logout()

# #     tab1, tab2 = st.tabs(["🎯 Prédiction", "📈 Statistiques"])

# #     with tab1:
# #         st.title("🚗 MNS Occasions")
# #         st.write("Obtenez une estimation par IA basée sur les données du marché.")

# #         if df_cars is not None:
# #             with st.form("prediction_form"):
# #                 col1, col2, col3 = st.columns(3)
                
# #                 with col1:
# #                     # Liste des marques uniques triées
# #                     list_brands = sorted(df_cars['Brand'].unique())
# #                     brand_selected = st.selectbox("Marque", list_brands)
                    
# #                     location = st.selectbox("Ville", ["Mumbai", "Hyderabad", "Kochi", "Coimbatore", "Delhi", "Kolkata", "Chennai", "Jaipur", "Bangalore", "Ahmedabad"])
# #                     fuel = st.selectbox("Carburant", ["Petrol", "Diesel", "CNG", "LPG"])
                
# #                 with col2:
# #                     # Filtrage dynamique des modèles selon la marque choisie
# #                     models_filtered = sorted(df_cars[df_cars['Brand'] == brand_selected]['Model'].unique())
# #                     model_selected = st.selectbox("Modèle", models_filtered)
                    
# #                     year = st.number_input("Année", min_value=1990, max_value=2026, value=2018)
# #                     transmission = st.selectbox("Boîte", ["Manual", "Automatic"])
                
# #                 with col3:
# #                     km = st.number_input("Kilométrage", min_value=0, value=50000)
# #                     power = st.number_input("Puissance (bhp)", min_value=0.0, value=75.0)
# #                     mileage = st.number_input("Consommation", min_value=0.0, value=20.0)

# #                 owner = st.selectbox("Propriétaire", ["First", "Second", "Third", "Fourth & Above"])
# #                 submit = st.form_submit_button("Estimer le prix")

# #             if submit:
# #                 payload = {
# #                     "Location": location,
# #                     "Year": int(year),
# #                     "Kilometers_Driven": int(km),
# #                     "Fuel_Type": fuel,
# #                     "Transmission": transmission,
# #                     "Owner_Type": owner,
# #                     "Mileage": float(mileage),
# #                     "Power": float(power),
# #                     "Model": model_selected,
# #                     "Brand": brand_selected
# #                 }

# #                 try:
# #                     with st.spinner('Analyse IA...'):
# #                         response = requests.post("http://127.0.0.1:8000/predict", json=payload)
# #                         prediction = response.json().get('predicted_price')

# #                         if prediction is not None:
# #                             # Conversion approximative (selon votre coefficient 929)
# #                             prix_euros = round(prediction * 929, 2)
# #                             st.success(f"### 💰 Prix estimé : {prix_euros} €")
# #                         else:
# #                             st.error("Erreur dans la réponse API.")
# #                 except Exception:
# #                     st.error("L'API FastAPI est éteinte (port 8000).")
# #         else:
# #             st.error("Impossible de charger les données pour les listes déroulantes.")

# #     with tab2:
# #         st.title("📈 Analyse du Marché")
# #         if df_cars is not None:
# #             marques = st.multiselect(
# #                 "Filtrer par marque",
# #                 options=df_cars['Brand'].unique(),
# #                 default=df_cars['Brand'].unique()[:5]
# #             )

# #             df_filtre = df_cars[df_cars['Brand'].isin(marques)]

# #             st.subheader("Relation Puissance vs Prix")
# #             fig = px.scatter(
# #                 df_filtre, x="Power", y="Price", size="Price",
# #                 color="Fuel_Type", hover_name="Model", size_max=40, template="plotly_dark"
# #             )
# #             st.plotly_chart(fig, use_container_width=True)

# #             st.subheader("Évolution des prix par Année")
# #             df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index()
# #             fig_line = px.line(df_evol, x="Year", y="Price", color="Brand", markers=True)
# #             st.plotly_chart(fig_line, use_container_width=True)
# #         else:
# #             st.error("Le fichier 'data/train_clean.csv' est introuvable.")


#************


# import streamlit as st
# import requests
# import pandas as pd 
# import plotly.express as px  # <--- CORRECTION 1 : import express

# # 1. Configuration de la page (UNE SEULE FOIS AU DÉBUT)
# st.set_page_config(page_title="MNS Occasions", layout="centered", page_icon="🚗")

# # --- GESTION DE LA SESSION (LOGIN) ---
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# def login_page():
#     st.title("🔐 Connexion")
#     with st.form("login_form"):
#         username = st.text_input("Nom d'utilisateur")
#         password = st.text_input("Mot de passe", type="password")
#         if st.form_submit_button("Se connecter"):
#             if username == "admin" and password == "123":
#                 st.session_state.logged_in = True
#                 st.rerun()
#             else:
#                 st.error("Identifiants incorrects.")

# def logout():
#     st.session_state.logged_in = False
#     st.rerun()

# # --- LOGIQUE D'AFFICHAGE ---
# if not st.session_state.logged_in:
#     login_page()
# else:
#     # Barre latérale
#     st.sidebar.title("Menu")
#     st.sidebar.write(f"Connecté en tant que : **admin**")
#     if st.sidebar.button("Déconnexion"):
#         logout()

#     # Création des onglets
#     tab1, tab2 = st.tabs(["🎯 Prédiction", "📈 Statistiques"])

#     # --- ONGLET 1 : PRÉDICTION ---
#     with tab1:
#         st.title("🚗 MNS Occasions")
#         st.write("Obtenez une estimation par IA en un clic.")

#         with st.form("prediction_form"):
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 brand = st.text_input("Marque", value="Maruti")
#                 location = st.selectbox("Ville", ["Mumbai", "Hyderabad", "Kochi", "Coimbatore", "Delhi", "Kolkata", "Chennai", "Jaipur", "Bangalore", "Ahmedabad"])
#                 fuel = st.selectbox("Carburant", ["Petrol", "Diesel", "CNG", "LPG"])
#             with col2:
#                 model_car = st.text_input("Modèle", value="Swift")
#                 year = st.number_input("Année", min_value=1990, max_value=2026, value=2018)
#                 transmission = st.selectbox("Boîte", ["Manual", "Automatic"])
#             with col3:
#                 km = st.number_input("Kilométrage", min_value=0, value=50000)
#                 power = st.number_input("Puissance (bhp)", min_value=0.0, value=75.0)
#                 mileage = st.number_input("Consommation", min_value=0.0, value=20.0)

#             owner = st.selectbox("Propriétaire", ["First", "Second", "Third", "Fourth & Above"])
#             submit = st.form_submit_button("Estimer le prix")

#         if submit:
#             payload = {
#                 "Location": location, "Year": int(year), "Kilometers_Driven": int(km),
#                 "Fuel_Type": fuel, "Transmission": transmission, "Owner_Type": owner,
#                 "Mileage": float(mileage), "Power": float(power), 
#                 "Model": model_car.upper(), "Brand": brand.upper()
#             }
#             try:
#                 with st.spinner('Analyse IA...'):
#                     response = requests.post("http://127.0.0.1:8000/predict", json=payload)
#                     prediction = response.json().get('predicted_price')
#                     st.success(f"### 💰 Prix estimé : {round(prediction * 929, 2)} €")
#             except Exception as e:
#                 st.error("L'API FastAPI est éteinte (port 8000).")

#     # --- ONGLET 2 : STATISTIQUES ---
#     with tab2:
#         st.title("📈 Analyse du Marché")
        
#         # On charge les données
#         try:
#             data = pd.read_csv('data/train_clean.csv') # Attention au chemin (slash /)

#             # Filtres graphiques (uniquement visibles dans cet onglet)
#             marques = st.multiselect("Filtrer par marque", options=data['Brand'].unique(), default=data['Brand'].unique()[:5])
#             df_filtre = data[data['Brand'].isin(marques)]

#             # Graphique 1
#             st.subheader("Relation Puissance vs Prix")
#             fig = px.scatter(
#                 df_filtre, x="Power", y="Price", size="Price", 
#                 color="Fuel_Type", hover_name="Brand", size_max=40,
#                 template="plotly_dark"
#             )
#             st.plotly_chart(fig, use_container_width=True)

#             # Graphique 2 (Evolution)
#             st.subheader("Évolution des prix par Année")
#             # Moyenne par année pour une courbe plus propre
#             df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index()
#             fig_line = px.line(df_evol, x="Year", y="Price", color="Brand", markers=True)
#             st.plotly_chart(fig_line, use_container_width=True)

#         except FileNotFoundError:
#             st.error("Le fichier 'data/train_clean.csv' est introuvable.")