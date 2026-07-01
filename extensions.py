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

from flask import Flask, request

app = Flask(__name__)


def get_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
        return ip.split(':')[0] if ':' in ip else ip
    raw = request.remote_addr or ''
    return raw.split(':')[0] if ':' in raw else raw


# celery = Celery(
#     "ims",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0",
#     include=["routes.common"]  # ← tells worker to import this module on startup
# )
