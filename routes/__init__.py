import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from .incident_base_routes import incident_base_bp
from flask_cors import CORS
from models import db


load_dotenv()

def register_routes(app):
    app.register_blueprint(incident_base_bp)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
    CORS(app, supports_credentials=True, origins=["http://localhost:5000"])

    db.init_app(app)

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app