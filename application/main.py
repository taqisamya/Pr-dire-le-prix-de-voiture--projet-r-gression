from fastapi import FastAPI, Query # pour pouvoir lancer dans le terminal  : 'pip install "fastapi[standard]"' puis 'fastapi dev main.py'
from pydantic import BaseModel, Field
import pandas as pd
from joblib import load

app = FastAPI()

model_ia = load("modele_svr.pkl")

@app.post("/predict")
def predict(data:pd.DataFrame):
    prediction = model_ia.predict(data[['Location','Year','Kilometers_Driven', 'Fuel_Type', 'Transmission', 'Owner_Type', 'Mileage','Power', 'Model', 'Brand']])[0]
    return prediction