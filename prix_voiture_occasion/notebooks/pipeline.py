import pandas as pd
import numpy as np
import re
 
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
 
def extract_number(text):   # fonction pour extraire les nombres des colonnes "Mileage", "Engine", "Power"
    if pd.isna(text):
        return np.nan
    match = re.findall(r'\d+', str(text))
    return int(match[0]) if match else np.nan
 
def supp_colum(df, columns_to_drop): # fonction pour supprimer les colonnes inutiles
    df.drop(columns=columns_to_drop, inplace=True)
    return df
 
 
 
def convert_new_price(df): # fonction pour convertir les prix en euros
    df["Price_Euros"] = df["Price"] * 0.009292 * 100000
    return df
 
def maj_brand(df): # fonction pour mettre les marques en majuscules
    df['Brand'] = df['Name'].str.split().str[0].str.upper()
    return df
 
def split_name(df): # fonction pour séparer la colonne "Name" en "Brand" et "Model"
    df['Brand'] = df['Name'].str.split().str[0]             # Premier mot
    df['Model'] = df['Name'].str.split().str[1:].str.join(' ')  # Le reste
    return df
 
 
def clean_data(df: pd.DataFrame) -> pd.DataFrame: # fonction pour nettoyer les données
    df=df.copy()
 
    df["Mileage"] = df["Mileage"].apply(extract_number)
    df["Engine"] = df["Engine"].apply(extract_number)
    df["Power"] = df["Power"].apply(extract_number)
    df["Price_Euros"] = df["Price"] * 0.009292 * 100000
    df['Brand'] = df['Name'].str.split().str[0].str.upper()
    df['Model'] = df['Name'].str.split().str[1:].str.join(' ')
    df.drop(columns=["Name", "Location", "Engine","Seats","New-price"], inplace=True)
    #Remplissage des valeurs manquantes par la moyenne
    numeric_cols = ["Year", "Kilometers_Driven", "Mileage", "Power", "Price_Euros"]
    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True)
    categorical_cols = ["Brand", "Model", "Fuel_Type", "Transmission", "Owner_Type"]
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)
   
 
 
def create_preprocessing_pipeline(df: pd.DataFrame) -> Pipeline: # fonction pour créer le pipeline de prétraitement
    numeric_features = [
        "Year",
        "Kilometers_Driven",
        "Mileage",
        "Power",
        "Price_Euros",
    ]
    categorical_features = [
        "Brand",
        "Model",
        "Fuel_Type",
        "Transmission",
        "Owner_Type",
    ]
 
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")
 
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
 
    pipeline = Pipeline(steps=[("preprocessor", preprocessor)])
    return pipeline
 
# préparer les données pour l'entraînement
def prepare_training_data(df: pd.DataFrame):
    df=clean_data(df)
    X = df.drop(columns=["Price_Euros"])
    y = df["Price_Euros"]
    return X, y
 
# Préparer les données pour pour la prediction
def prepare_prediction_data(features:dict)):
    df=clean_data(df)
    X = df.drop(columns=["Price_Euros"])
    return X