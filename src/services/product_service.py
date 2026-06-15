"""Módulo de servicios de productos - CRUD de productos con validaciones de negocio"""

import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from src.models.product import Product

logger = logging.getLogger(__name__)


def create_product(session: Session, name: str, cost: Decimal, price: Decimal, cant: int = 0) -> Product:
    """Crea un nuevo producto validando nombre, costo y precio; persiste en la base de datos"""
    if not name:
        raise ValueError("Nombre: el nombre del producto no puede estar vacío")
    if cost <= 0:
        raise ValueError("Costo: debe ser un número positivo")
    if price <= 0:
        raise ValueError("Precio: debe ser un número positivo")
    product = Product(name=name, cost=cost, price=price, cant=cant)
    session.add(product)
    session.commit()
    return product


def get_product(session: Session, product_id: int) -> Product | None:
    """Busca un producto por su ID; retorna None si no existe"""
    return session.query(Product).filter(Product.id_prod == product_id).first()


def get_all_products(session: Session) -> list[Product]:
    """Obtiene todos los productos ordenados por ID"""
    return session.query(Product).order_by(Product.id_prod).all()


def update_product(session: Session, product_id: int, **kwargs) -> Product | None:
    """Actualiza los atributos de un producto existente usando kwargs; retorna None si no se encuentra"""
    product = get_product(session, product_id)
    if not product:
        return None
    for key, value in kwargs.items():
        if hasattr(product, key):
            setattr(product, key, value)
    session.commit()
    return product


def delete_product(session: Session, product_id: int) -> bool:
    """Elimina un producto por ID; retorna False si no existe, True si se eliminó correctamente"""
    product = get_product(session, product_id)
    if not product:
        return False
    session.delete(product)
    session.commit()
    return True
