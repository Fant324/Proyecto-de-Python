"""Modelo de venta - tabla 'sell' para registrar ventas realizadas"""

import logging
from sqlalchemy import Column, Integer, Numeric, Date
from src.database.base import Base

logger = logging.getLogger(__name__)


class Sell(Base):
    """Modelo que representa una venta con cantidad total de unidades, ingreso generado y fecha"""
    __tablename__ = "sell"

    idSell = Column(Integer, primary_key=True, autoincrement=True)
    cant = Column(Integer, nullable=False)
    revenue = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
