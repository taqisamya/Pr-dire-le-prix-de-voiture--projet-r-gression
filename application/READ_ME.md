Application de prédiction les tarifs des vihécules
 
Ce projet est pour objectif de concevoir une application pour prédire/estimer le prix de  voiture d'occasion à l'aide d'un modèle de machine learning (SVR/ support vector regression).
 
Elle propose une interactive avec authentification, visualisation des tendances du marché (EDA).
 
si le projet est récupérer depuis GitHub, il est nécessaire:
1. créer un environnement en tapant (python -m venv venv)
2. activer l'environnement sur:
Windows:venv\Scripts\activate
linux/Mac: source venv/bin/activate
 
3. installer les bibliothèques: pip install pandas scikit-learn matplotlib joblib streamlit fastapi uvicorn plotly
 
4. pour le lancement de l'application, elle utilise une architecture API + utilisateur, donc il faut lancer deux terminaux:
 
-lancer FastAPI : uvicorn main:app --reload
-lancer Streamlit: streamlit run app_streamlit.py
 
l'interface s'ouvrira automatiquement dans votre navigateur, accueilli par une page d'accueil avec un bouton de login , après  la connexion on passe directement au coeur de l'application avec deux onglets estimer le prix et statistiques.