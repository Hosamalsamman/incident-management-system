from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import firebase_admin
from firebase_admin import credentials

socketio = SocketIO(cors_allowed_origins="*")

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

cred = credentials.Certificate("firebase-service-account.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)