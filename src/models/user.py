"""Modelo de usuario - tabla 'users' para autenticación y control de roles"""

import logging
from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from src.database.base import Base

logger = logging.getLogger(__name__)


class User(Base):
    """Modelo que representa un usuario del sistema con username, password hasheada y rol (admin/vendedor)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("admin", "almacen", "vendedor", name="user_roles"), nullable=False, default="vendedor")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
