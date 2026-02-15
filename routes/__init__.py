import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from werkzeug.exceptions import RequestEntityTooLarge

from .current_incidents import current_incident_bp
from .incident_base_routes import incident_base_bp
from flask_cors import CORS
from extensions import db
from routes import incident_socket
from extensions import socketio



load_dotenv()

def register_routes(app):
    app.register_blueprint(incident_base_bp)
    app.register_blueprint(current_incident_bp)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
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