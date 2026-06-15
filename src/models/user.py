"""Modelo de usuario - tabla 'users' para autenticación y control de roles"""

import logging
from sqlalchemy import Column, Integer, String, Enum
from src.database.base import Base

logger = logging.getLogger(__name__)


class User(Base):
    """Modelo que representa un usuario del sistema con username, password hasheada y rol (admin/vendedor)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("admin", "vendedor", name="user_roles"), nullable=False, default="vendedor")
