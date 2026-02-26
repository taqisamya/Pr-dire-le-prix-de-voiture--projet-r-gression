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