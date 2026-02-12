import pandas as pd
import joblib

# ============================
# Charger modèle entraîné
# ============================

model = joblib.load("top_model.pkl")
print("Modèle chargé.")

# ============================
# Charger données à prédire
# ============================

df_predict = pd.read_csv(r"data\predict_clean.csv")

print(f"{len(df_predict)} lignes à prédire")

# ============================
# Prédictions
# ============================

predictions = model.predict(df_predict)

# Ajouter colonne prédite
df_predict["Predicted_Price"] = predictions.round(2)

# ============================
# Sauvegarde
# ============================

output_path = r"data\predictions.csv"
df_predict.to_csv(output_path, index=False)

print("Prédictions enregistrées :", output_path)