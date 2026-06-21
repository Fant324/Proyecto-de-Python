"""Módulo de servicios de stock - operaciones atómicas de actualización y consulta de inventario"""

import logging
from sqlalchemy.orm import Session
from src.models.product import Product

logger = logging.getLogger(__name__)


def add_stock(session: Session, product_id: int, quantity: int) -> None:
    """Incrementa el stock de un producto usando bloqueo pesimista (with_for_update) para evitar condiciones de carrera"""
    product = session.query(Product).filter_by(id_prod=product_id).with_for_update().one()
    product.cant += quantity


def remove_stock(session: Session, product_id: int, quantity: int) -> None:
    """Decrementa el stock de un producto usando bloqueo pesimista para mantener la consistencia"""
    product = session.query(Product).filter_by(id_prod=product_id).with_for_update().one()
    product.cant -= quantity


def get_stock(session: Session, product_id: int) -> int | None:
    """Consulta el stock actual de un producto; retorna None si el producto no existe"""
    product = session.query(Product).filter_by(id_prod=product_id).first()
    if product is None:
        return None
    return product.cant
