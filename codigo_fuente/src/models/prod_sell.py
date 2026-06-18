"""Modelo de relación producto-venta - tabla 'prod_sell' para asociar productos con ventas"""

import logging
from sqlalchemy import Column, Integer, ForeignKey
from src.database.base import Base

logger = logging.getLogger(__name__)


class ProdSell(Base):
    """Modelo asociativo que vincula productos con ventas, incluyendo la cantidad vendida de cada producto"""
    __tablename__ = "prod_sell"

    id_prod = Column(Integer, ForeignKey("product.id_prod"), primary_key=True)
    idSell = Column(Integer, ForeignKey("sell.idSell"), primary_key=True)
    cant = Column(Integer, nullable=False)
