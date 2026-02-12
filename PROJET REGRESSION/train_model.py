import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, RandomizedSearchCV, learning_curve
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from preprocessing import create_preprocessing_pipeline

# ============================
# Charger les données
# ============================

df_train = pd.read_csv(r"data\train_clean.csv")

# Séparer X / Y
X = df_train.drop(columns=["Price"])
Y = df_train["Price"]

# Split train / test
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

# ============================
# Préprocesseur
# ============================

preprocessor = create_preprocessing_pipeline(X)

# ============================
# Pipeline modèle
# ============================

model_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", Ridge())
])

# ============================
# Random Search
# ============================

param_dist = {
    "regressor__alpha": np.logspace(-3, 3, 50),
    "regressor__solver": ["auto", "svd", "cholesky"]
}

random_search = RandomizedSearchCV(
    model_pipeline,
    param_distributions=param_dist,
    n_iter=20,
    cv=5,
    scoring="r2",
    random_state=42,
    n_jobs=-1
)

# Entraînement
random_search.fit(X_train, Y_train)

best_model = random_search.best_estimator_

print("Meilleurs paramètres :", random_search.best_params_)

# ============================
# Évaluation
# ============================

Y_pred = best_model.predict(X_test)

mse = mean_squared_error(Y_test, Y_pred)
rmse = root_mean_squared_error(Y_test, Y_pred)
r2 = r2_score(Y_test, Y_pred)

print(f"MSE : {mse:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R² : {r2:.3f}")

# ============================
# Sauvegarde modèle final
# ============================

joblib.dump(best_model, "top_model.pkl")
print("Modèle sauvegardé : top_model.pkl")

# ============================
# Courbe d'apprentissage
# ============================

train_sizes, train_scores, val_scores = learning_curve(
    best_model,
    X,
    Y,
    cv=5,
    scoring="r2",
    train_sizes=np.linspace(0.1, 1.0, 10),
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

plt.figure(figsize=(8,5))
plt.plot(train_sizes, train_mean, marker="o", label="Train")
plt.plot(train_sizes, val_mean, marker="o", label="Validation")

plt.xlabel("Nombre d'échantillons")
plt.ylabel("R²")
plt.title("Courbe d'apprentissage Ridge")
plt.legend()
plt.grid(True)
plt.show()
