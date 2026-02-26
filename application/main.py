from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import joblib
import pandas as pd
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Annotated

class CarData(BaseModel):
    Location: str = Field(..., description="Ville", examples=["Mumbai"])
    Year: int = Field(..., description="Année", examples=[2010])
    Kilometers_Driven: int = Field(..., description="KM parcourus", examples=[10000])
    Fuel_Type: str = Field(..., description="Carburant", examples=["Diesel"])
    Transmission: str = Field(..., description="Boîte", examples=["Manual"])
    Owner_Type: str = Field(..., description="Main", examples=["First"])
    Mileage: float = Field(..., description="Consommation", examples=[20.0])
    Power: float = Field(..., description="Puissance bhp", examples=[50.0])
    Model: str = Field(..., description="Modèle", examples=["1000 AC"])
    Brand: str = Field(..., description="Marque", examples=["MARUTI"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    path = Path("models/modele_svr.pkl")
    if path.exists():
        app.state.model = joblib.load(path)
        print("✅ Modèle SVR chargé.")
    else:
        app.state.model = None
        print("❌ Modèle introuvable.")
    yield

app = FastAPI(lifespan=lifespan, title="Prédiction prix de voitures")

@app.post("/prediction", tags=["Modèle de prédiction de prix"], summary="Prédiction de prix de voitures d'occasion à partir des informations renseignées")
async def predict(data: Annotated[CarData, Depends()]):
    if app.state.model is None:
        return {"error": "Modèle non chargé"}
        
    df = pd.DataFrame([data.model_dump()])
    prediction = app.state.model.predict(df)[0]
    return {"predicted_price": float(prediction)}