"""Modelo de producto - tabla 'product' para el catálogo de productos del inventario"""

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from sqlalchemy.sql import func
from src.database.base import Base

logger = logging.getLogger(__name__)


class Product(Base):
    """Modelo que representa un producto con nombre, cantidad en stock, costo y precio de venta"""
    __tablename__ = "product"

    id_prod = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    cant = Column(Integer, nullable=False, default=0)
    cost = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
