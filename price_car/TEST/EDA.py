import matplotlib.pyplot as plt
import seaborn as sns 
import pandas as pd
import io
import base64 
import os
import base64
from io import BytesIO

def matrice_correlation():
    base_dir=os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "train_clean.csv")
    df=pd.read_csv(data_path)
    df["Fuel_Type"]=pd.factorize(df["Fuel_Type"])[0]
    df["Transmission"]=pd.factorize(df["Transmission"])[0]
    df["Owner_Type"]=pd.factorize(df["Owner_Type"])[0]
    df["Brand"]=pd.factorize(df["Brand"])[0]
    df["Model"]=pd.factorize(df["Model"])[0]
    df["Location"]=pd.factorize(df["Location"])[0]
    correlation= df.corr()
    plt.figure(figsize=(10,8))
    sns.heatmap(correlation, annot=True ,fmt=".2f", cmap="coolwarm")
    plt.title("la matrice de corrélation ")
    buf = io.BytesIO() # Créer un buffer mémoire
    plt.savefig(buf, format='png', bbox_inches='tight') # Sauvegarder la figure dans le buffer
    buf.seek(0) # Revenir au début du buffer
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8') # Encoder en base64
    plt.close()
    return img_base64
import matplotlib
matplotlib.use("Agg")



def prix_annee():
    base_dir=os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "train_clean.csv")
    df=pd.read_csv(data_path)

    # Calcul du prix moyen par année
    prix_moyen = df.groupby("Year")["Price"].mean()

    plt.figure(figsize=(10,5))
    prix_moyen.plot()

    plt.title("Prix moyen en fonction de l'année")
    plt.xlabel("Année")
    plt.ylabel("Prix moyen")

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    plt.close()

    return image_base64
