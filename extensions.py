from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import firebase_admin
from firebase_admin import credentials
# from celery import Celery

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

cred = credentials.Certificate("firebase-service-account.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


# celery = Celery(
#     "ims",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0",
#     include=["routes.common"]  # ← tells worker to import this module on startup
# )
