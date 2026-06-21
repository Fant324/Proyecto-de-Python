"""Módulo de servicios de stock - consulta de inventario"""

from sqlalchemy.orm import Session
from src.models.product import Product


def get_stock(session: Session, product_id: int) -> int | None:
    """Consulta el stock actual de un producto; retorna None si el producto no existe"""
    product = session.query(Product).filter_by(id_prod=product_id).first()
    if product is None:
        return None
    return product.cant
