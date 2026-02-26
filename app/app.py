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
#     """)
#     # On crée un compte admin par défaut pour le test (password: admin123)
#     admin_user = "admin"
#     admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
#     cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (admin_user, admin_pass))
#     conn.commit()
#     conn.close()

# create_db()

# @st.cache_data
# def load_car_data():
#     try:
#         df = pd.read_csv('data/train_clean.csv')
#         df['Brand'] = df['Brand'].str.upper()
#         df['Model'] = df['Model'].str.upper()
#         return df
#     except Exception:
#         return None

# df_cars = load_car_data()

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def login_user(username, password):
#     conn = sqlite3.connect("users.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
#     data = cursor.fetchone()
#     conn.close()
#     return data

# # =============================
# # SESSION
# # =============================
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "username" not in st.session_state:
#     st.session_state.username = ""

# # =============================
# # LOGIQUE D'AFFICHAGE
# # =============================
# if not st.session_state.logged_in:
#     st.title("🔐 Connexion")
#     tab_login, tab_sign = st.tabs(["Connexion", "Inscription"])
    
#     with tab_login:
#         user_in = st.text_input("Utilisateur")
#         pass_in = st.text_input("Mot de passe", type="password")
#         if st.button("Se connecter"):
#             user = login_user(user_in, pass_in)
#             if user:
#                 st.session_state.logged_in = True
#                 st.session_state.username = user_in
#                 st.rerun()
#             else:
#                 st.error("Échec de connexion.")
# else:
#     # Barre latérale
#     st.sidebar.title("🚗 MNS Panel")
#     st.sidebar.info(f"Session : **{st.session_state.username}**")
#     if st.sidebar.button("Déconnexion"):
#         st.session_state.logged_in = False
#         st.rerun()

#     # Définition des onglets (L'onglet Admin n'apparaît que pour l'admin)
#     tabs_list = ["🎯 Prédiction", "📈 Statistiques"]
#     if st.session_state.username.lower() == "admin":
#         tabs_list.append("⚙️ Admin (Algo)")
    
#     tabs = st.tabs(tabs_list)

#     # --- ONGLET 1 : PRÉDICTION ---
#     with tabs[0]:
#         st.header("Estimation de véhicule")
#         if df_cars is not None:
#             with st.form("predict_form"):
#                 c1, c2 = st.columns(2)
#                 brand = c1.selectbox("Marque", sorted(df_cars['Brand'].unique()))
#                 model = c2.selectbox("Modèle", sorted(df_cars[df_cars['Brand'] == brand]['Model'].unique()))
#                 year = c1.slider("Année", 2000, 2026, 2018)
#                 km = c2.number_input("Kilométrage", value=50000)
#                 fuel = c1.selectbox("Carburant", ["Petrol", "Diesel", "CNG", "LPG"])
#                 trans = c2.selectbox("Boîte", ["Manual", "Automatic"])
#                 power = st.number_input("Puissance (bhp)", value=100.0)
                
#                 if st.form_submit_button("Calculer le prix"):
#                     # Logique d'appel API ici...
#                     st.success("Appel API simulé vers /predict")
#         else:
#             st.warning("Données indisponibles.")

#     # --- ONGLET 2 : STATS ---
#     with tabs[1]:
#         st.header("Analyse du marché")
#         if df_cars is not None:
#             brand_filter = st.multiselect("Marques", df_cars['Brand'].unique(), default=df_cars['Brand'].unique()[0])
#             fig = px.histogram(df_cars[df_cars['Brand'].isin(brand_filter)], x="Price", color="Brand", barmode="overlay")
#             st.plotly_chart(fig, use_container_width=True)

#     # --- ONGLET 3 : ADMIN (MODIFICATION ALGO) ---
#     if st.session_state.username.lower() == "admin":
#         with tabs[2]:
#             st.header("🛠 Configuration de l'IA")
#             st.write("Ajustez les paramètres d'entraînement du modèle (XGBoost/RandomForest)")
            
#             col_a, col_b = st.columns(2)
#             with col_a:
#                 algo_type = st.selectbox("Algorithme cible", ["Random Forest", "XGBoost", "Linear Regression"])
#                 n_estimators = st.slider("Nombre d'arbres (n_estimators)", 10, 500, 100)
#             with col_b:
#                 max_depth = st.slider("Profondeur max (max_depth)", 1, 50, 10)
#                 learning_rate = st.number_input("Taux d'apprentissage", value=0.1, step=0.01)

#             st.divider()
            
#             c1, c2 = st.columns(2)
#             if c1.button("🚀 Réentraîner le modèle"):
#                 # Ici on simule l'envoi des paramètres à FastAPI pour lancer un entraînement
#                 update_payload = {
#                     "algo": algo_type,
#                     "params": {"n_estimators": n_estimators, "max_depth": max_depth, "lr": learning_rate}
#                 }
#                 with st.spinner("Réentraînement en cours..."):
#                     # requests.post("http://127.0.0.1:8000/retrain", json=update_payload)
#                     st.success(f"Modèle {algo_type} mis à jour avec succès !")

#             if c2.button("💾 Sauvegarder la configuration"):
#                 st.toast("Configuration sauvegardée dans la base de données.")

#             st.info("Note : Le réentraînement peut prendre plusieurs minutes selon la taille du dataset.")






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
        st.title("🚗 MNS Occasions")
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

    with tab2:
        st.title("📈 Analyse du Marché")
        if df_cars is not None:
            marques = st.multiselect(
                "Filtrer par marque",
                options=df_cars['Brand'].unique(),
                default=df_cars['Brand'].unique()[:5]
            )

            df_filtre = df_cars[df_cars['Brand'].isin(marques)]

            st.subheader("Relation Puissance vs Prix")
            fig = px.scatter(
                df_filtre, x="Power", y="Price", size="Price",
                color="Fuel_Type", hover_name="Model", size_max=40, template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Évolution des prix par Année")
            df_evol = df_filtre.groupby(['Year', 'Brand'])['Price'].mean().reset_index()
            fig_line = px.line(df_evol, x="Year", y="Price", color="Brand", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.error("Le fichier 'data/train_clean.csv' est introuvable.")


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