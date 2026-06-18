"""Módulo de base declarativa de SQLAlchemy - clase base para todos los modelos ORM"""

import logging
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos del sistema de inventario"""
    pass
