"""Modelo de salida - tabla 'out' para registrar salidas de productos del inventario"""

import logging
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from src.database.base import Base

logger = logging.getLogger(__name__)


class Out(Base):
    """Modelo que representa una salida de producto con destino, cantidad y fecha"""
    __tablename__ = "out"

    idOut = Column(Integer, primary_key=True, autoincrement=True)
    id_prod = Column(Integer, ForeignKey("product.id_prod"), nullable=False)
    cant = Column(Integer, nullable=False)
    destination = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
