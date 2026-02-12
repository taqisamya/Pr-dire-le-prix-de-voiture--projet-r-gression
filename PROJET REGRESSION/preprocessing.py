import pandas as pd
import numpy as np
import re

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

# ------------------------------
# Chargement des données
# ------------------------------
df = pd.read_csv(r"data\train.csv")

# ------------------------------
# Nettoyage initial
# ------------------------------

# Supprimer voitures électriques
df = df[df['Fuel_Type'] != 'Electric'].reset_index(drop=True)

# Supprimer voitures spécifiques
voitures_a_supprimer = [
    "Smart Fortwo CDI AT",
    "Ambassador Classic Nova Diesel",
    "Bentley Continental Flying Spur",
    "Lamborghini Gallardo Coupe"
]
df = df[~df['Name'].isin(voitures_a_supprimer)].reset_index(drop=True)

# ------------------------------
# Fonctions utilitaires
# ------------------------------

def extract_number(text):
    """Extraire le premier nombre d'une chaîne"""
    if pd.isna(text):
        return np.nan
    match = re.findall(r'\d+', str(text))
    return int(match[0]) if match else np.nan
    


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage complet du DataFrame"""
    df = df.copy()

    # Extraire les nombres
    df["Mileage"] = df["Mileage"].apply(extract_number)
    df["Engine"] = df["Engine"].apply(extract_number)
    df["Power"] = df["Power"].apply(extract_number)
    df['Mileage'] = df['Mileage'].astype(float)

    # # Conversion du prix
    # df["Price"] = (df["Price"] * 0.009292 * 100000).round(2)

    # Brand et Model
    df['Brand'] = df['Name'].str.split().str[0].str.upper()
    df['Model'] = df['Name'].str.split().str[1:].str.join(' ').str.upper()

    # Supprimer les colonnes inutiles
    cols_to_drop = ["Name", "Engine", "Seats", "New_Price"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    # Remplissage des valuers manquantes
    numeric_cols = ["Year", "Kilometers_Driven", "Mileage"]
    for col in numeric_cols:
        if col in df.columns:
            df[col].fillna(df[col].median(), inplace=True)
    df["Power"] = df["Power"].fillna(df["Power"].median(), inplace=False)

    categorical_cols = ["Brand", "Model", "Fuel_Type", "Transmission", "Owner_Type"]
    for col in categorical_cols:
        if col in df.columns:
            df[col].fillna(df[col].mode()[0], inplace=True)

    return df


def create_preprocessing_pipeline(df):

    numeric_features = [
        "Year",
        "Kilometers_Driven",
        "Mileage",
        "Power"
    ]

    categorical_features = [
        "Brand",
        "Model",
        "Fuel_Type",
        "Transmission",
        "Owner_Type"
    ]

    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    return preprocessor


def prepare_training_data(df: pd.DataFrame):
    """Préparer les features X et target y"""
    df = clean_data(df)
    X = df.drop(columns=["Price"])
    y = df["Price"]
    return X, y


def prepare_prediction_data(features: dict) -> pd.DataFrame:
    """Préparer les données d'entrée pour une prédiction"""
    df = pd.DataFrame([features])

    # Nettoyage
    df["Mileage"] = df["Mileage"].apply(extract_number)
    df["Engine"] = df["Engine"].apply(extract_number)
    df["Power"] = df["Power"].apply(extract_number)

    # Brand et Model
    df['Brand'] = df['Name'].str.split().str[0].str.upper()
    df['Model'] = df['Name'].str.split().str[1:].str.join(' ')

    # Supprimer colonnes inutiles si elles existent
    cols_to_drop = ["Name", "Location", "Engine", "Seats", "New-price", "Price"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    # Remplissage des valeurs manquantes
    numeric_cols = ["Year", "Kilometers_Driven", "Mileage", "Power"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    categorical_cols = ["Brand", "Model", "Fuel_Type", "Transmission", "Owner_Type"]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])

    return df

# ------------------------------
# Préparer et enregistrer les fichiers CSV
# ------------------------------

# Nettoyer entièrement les données pour l'entraînement
df_train = clean_data(df)

# Séparer features et target pour l'entraînement
X_train = df_train.drop(columns=["Price"])
y_train = df_train["Price"]

# Enregistrer CSV pour l'entraînement
train_csv_path = r"C:\Users\mohamd.arjoune\OneDrive - LYCEE Jules Haag\Bureau\PROJET REGRESSION\data\train_clean.csv"
df_train.to_csv(train_csv_path, index=False)
print(f"CSV d'entraînement enregistré : {train_csv_path}")

# Préparer un CSV "prediction" sans la colonne cible Price
df_predict = X_train.copy()  # on garde les mêmes colonnes que X_train
predict_csv_path = r"C:\Users\mohamd.arjoune\OneDrive - LYCEE Jules Haag\Bureau\PROJET REGRESSION\data\predict_clean.csv"
df_predict.to_csv(predict_csv_path, index=False)
print(f"CSV de prédiction enregistré : {predict_csv_path}")