import os
from datetime import timedelta

from flask import Flask, jsonify
from dotenv import load_dotenv
from werkzeug.exceptions import RequestEntityTooLarge

from .current_incidents import current_incident_bp
from .gis_date_route import gis_bp
from .incident_base_routes import incident_base_bp
from flask_cors import CORS
from extensions import db
from routes import incident_socket
from extensions import socketio
from .users import users_bp
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

load_dotenv()

def register_routes(app):
    app.register_blueprint(incident_base_bp)
    app.register_blueprint(current_incident_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(gis_bp)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize JWT
    app.config['JWT_SECRET_KEY'] = os.getenv("FLASK_KEY")
    # Access token: 30 days
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    jwt = JWTManager(app)

    CORS(app, supports_credentials=True, origins=["http://localhost:5000"])

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(e):
        return jsonify({"error": "الصورة أكبر من الحجم المسموح (5MB)"}), 413

    db.init_app(app)
    socketio.init_app(app)

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app