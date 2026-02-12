import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///cars.db"  # simple pour commencer
    SQLALCHEMY_TRACK_MODIFICATIONS = False

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from models import Car
    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return {"message": "API voitures OK"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


