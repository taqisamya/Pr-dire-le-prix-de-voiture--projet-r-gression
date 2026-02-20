from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Nécessaire pour les sessions

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèle Utilisateur simple
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Utilisateur fictif pour l'exemple
users = {'admin': {'password': '123'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

# Chargement du modèle IA
model_ia = joblib.load('modele_test.pkl')

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Identifiants invalides')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    # ... (Garder le même code de prédiction que précédemment)
    data = {
        'Location': request.form['location'],
        'Year': int(request.form['year']),
        'Kilometers_Driven': float(request.form['km']),
        'Fuel_Type': request.form['fuel'],
        'Transmission': request.form['transmission'],
        'Owner_Type': request.form['owner'],
        'Mileage': float(request.form['mileage']),
        'Power': float(request.form['power']),
        'Model': request.form['model'].upper(),
        'Brand': request.form['brand'].upper()
    }
    df_input = pd.DataFrame([data])
    
    prediction = model_ia.predict(df_input[['Location','Year','Kilometers_Driven', 'Fuel_Type', 'Transmission', 'Owner_Type', 'Mileage','Power', 'Model', 'Brand']])[0]
    
    return render_template('index.html', prediction=round(prediction, 2))

if __name__ == '__main__':
    app.run(debug=True)