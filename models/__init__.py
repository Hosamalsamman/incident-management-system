from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, NVARCHAR, Numeric, DECIMAL
from flask_login import UserMixin
from .users_and_authentication import User, Group, AuthorityLevel
from .sectors import SectorManagement, SectorBranch, SectorClassification



