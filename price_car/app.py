from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 as sql
from TEST.EDA import matrice_correlation , prix_annee

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"


# -----------------------------
# INITIALISATION BASE SQLITE
# -----------------------------
def create_db():
    conn = sql.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_db()


# -----------------------------
# PAGE ACCUEIL
# -----------------------------
@app.route("/")
def accueil():
    return render_template("accueil.html")


# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = sql.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            flash("Inscription réussie ! Connectez-vous.")
            return redirect(url_for("login"))

        except sql.IntegrityError:
            flash("Utilisateur déjà existant.")

        finally:
            conn.close()

    return render_template("register.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sql.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect(url_for("EDA"))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.")

    return render_template("login.html")

# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        flash("Fonctionnalité non implémentée pour le moment.")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")
# -----------------------------
# EDA (PROTÉGÉ)
# -----------------------------
@app.route("/EDA")
def EDA():
    if "user" not in session:
        flash("Veuillez vous connecter d'abord.")
        return redirect(url_for("login"))

    corr_img = matrice_correlation()
    graph_prix = prix_annee()

    return render_template(
        "EDA.html",
        corr_img=corr_img,
        graph_prix = graph_prix
    )


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Vous êtes déconnecté.")
    return redirect(url_for("login"))


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)





# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from TEST.EDA import matrice_correlation

# app = Flask(__name__)
# app.secret_key = "super_secret_key_change_this"  # IMPORTANT pour les sessions

# # Simule une base de données temporaire (à remplacer plus tard par MySQL)
# users = {
#     "admin": generate_password_hash("1234")
# }


# @app.route("/")
# def accueil():
#     return render_template("accueil.html")


# # ---------------- LOGIN ----------------
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         if username in users and check_password_hash(users[username], password):
#             session["user"] = username
#             return redirect(url_for("EDA"))
#         else:
#             flash("Nom d'utilisateur ou mot de passe incorrect")

#     return render_template("login.html")


# # ---------------- REGISTER ----------------
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         confirm_password = request.form["confirm_password"]
        


#         if password != confirm_password:
#             flash("Les mots de passe ne correspondent pas.")
#             return redirect(url_for("register"))

#         if username in users:
#             flash("Utilisateur déjà existant")
#         else:
#             hashed_password = generate_password_hash(password)
#             users[username] = hashed_password
#             flash("Inscription réussie ! Connectez-vous.")
#             return redirect(url_for("login"))

#     return render_template("register.html")



# # ---------------- FORGOT PASSWORD ----------------
# @app.route("/forgot_password", methods=["GET", "POST"])
# def forgot_password():
#     if request.method == "POST":
#         flash("Fonctionnalité non implémentée pour le moment.")
#         return redirect(url_for("login"))

#     return render_template("forgot_password.html")


# # ---------------- EDA  ----------------
# @app.route('/EDA')
# def EDA():
#     if "user" not in session:
#         flash("Veuillez vous connecter d'abord.")
#         return redirect(url_for("login"))

#     corr_img = matrice_correlation()
#     return render_template(
#         'EDA.html',
#         matrice_correlation=corr_img
#     )


# # ---------------- LOGOUT ----------------
# @app.route("/logout")
# def logout():
#     session.pop("user", None)
#     flash("Vous êtes déconnecté.")
#     return redirect(url_for("login"))


# if __name__ == "__main__":
#     app.run(debug=True)

