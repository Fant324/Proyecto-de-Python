"""Modelo de entrada - tabla 'entry' para registrar ingresos de productos al inventario"""

import logging
from sqlalchemy import Column, Integer, ForeignKey, Date
from src.database.base import Base

logger = logging.getLogger(__name__)


class Entry(Base):
    """Modelo que representa una entrada de producto con referencia al producto, cantidad y fecha"""
    __tablename__ = "entry"

    idEntry = Column(Integer, primary_key=True, autoincrement=True)
    id_prod = Column(Integer, ForeignKey("product.id_prod"), nullable=False)
    cant = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
