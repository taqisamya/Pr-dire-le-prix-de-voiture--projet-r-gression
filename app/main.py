# from fastapi import FastAPI, HTTPException
# from contextlib import asynccontextmanager
# import joblib
# import pandas as pd
# from pathlib import Path
# from pydantic import BaseModel
# from sklearn.svm import SVR
# from sklearn.ensemble import RandomForestRegressor
# import os

# # Modèle de données pour la prédiction
# class CarData(BaseModel):
#     Location: str
#     Year: int
#     Kilometers_Driven: float
#     Fuel_Type: str
#     Transmission: str
#     Owner_Type: str
#     Mileage: float
#     Power: float
#     Model: str
#     Brand: str

# # Modèle de données pour le réentraînement
# class RetrainParams(BaseModel):
#     algo: str
#     params: dict

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Chargement initial
#     path = Path("models/modele_svr.pkl")
#     if path.exists():
#         app.state.model = joblib.load(path)
#         print("✅ Modèle chargé au démarrage.")
#     else:
#         app.state.model = None
#         print("⚠️ Aucun modèle trouvé. En attente d'un entraînement.")
#     yield
#     app.state.model = None

# app = FastAPI(lifespan=lifespan)

# @app.post("/predict")
# async def predict(data: CarData):
#     if app.state.model is None:
#         raise HTTPException(status_code=400, detail="Modèle non disponible. Veuillez le réentraîner.")
    
#     # Transformation des données en DataFrame
#     df = pd.DataFrame([data.model_dump()])
    
#     # Prétraitement : Votre modèle attend probablement des colonnes encodées.
#     # Assurez-vous que le pipeline dans le .pkl gère le OneHotEncoding/Scaling.
#     try:
#         prediction = app.state.model.predict(df)[0]
#         return {"predicted_price": float(prediction)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {str(e)}")

# @app.post("/retrain")
# async def retrain(config: RetrainParams):
#     try:
#         # 1. Charger les données propres
#         data_path = "data/train_clean.csv"
#         if not os.path.exists(data_path):
#             raise HTTPException(status_code=404, detail="Fichier data/train_clean.csv introuvable.")
        
#         df = pd.read_csv(data_path)
        
#         # Séparation X et y (adaptez selon vos noms de colonnes réels)
#         X = df.drop(columns=['Price'])
#         y = df['Price']
        
#         # 2. Choisir l'algorithme selon le panel Admin
#         if config.algo == "Random Forest":
#             new_model = RandomForestRegressor(
#                 n_estimators=config.params.get("n_estimators", 100),
#                 max_depth=config.params.get("max_depth", 10)
#             )
#         else: # Par défaut SVR
#             new_model = SVR(C=config.params.get("C", 1.0))
            
#         # 3. Entraînement (Note: Idéalement, utilisez un Pipeline scikit-learn ici)
#         # Pour cet exemple, on suppose que le modèle contient déjà le preprocessing
#         new_model.fit(X, y)
        
#         # 4. Sauvegarder et mettre à jour le modèle en mémoire
#         model_path = "models/modele_svr.pkl"
#         joblib.dump(new_model, model_path)
#         app.state.model = new_model
        
#         return {"status": "success", "message": f"Modèle {config.algo} réentraîné et mis à jour."}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




from fastapi import FastAPI
from contextlib import asynccontextmanager
import joblib
import pandas as pd
from pathlib import Path
from pydantic import BaseModel

class CarData(BaseModel):
    Location: str
    Year: int
    Kilometers_Driven: float
    Fuel_Type: str
    Transmission: str
    Owner_Type: str
    Mileage: float
    Power: float
    Model: str
    Brand: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chargement sécurisé
    path = Path("models/modele_svr.pkl")
    if path.exists():
        app.state.model = joblib.load(path)
        print("✅ Modèle SVR chargé avec succès.")
    else:
        print("❌ ERREUR : Fichier modèle introuvable !")
    yield
    app.state.model = None

app = FastAPI(lifespan=lifespan)

@app.post("/predict")
async def predict(data: CarData):
    df = pd.DataFrame([data.model_dump()]) # model_dump remplace dict() en 2026
    prediction = app.state.model.predict(df)[0]
    return {"predicted_price": float(prediction)}