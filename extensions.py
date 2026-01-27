from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

socketio = SocketIO(cors_allowed_origins="*")

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)