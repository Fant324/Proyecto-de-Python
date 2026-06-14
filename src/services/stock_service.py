from sqlalchemy.orm import Session
from src.models.product import Product


def add_stock(session: Session, product_id: int, quantity: int) -> None:
    product = session.query(Product).filter_by(id_prod=product_id).with_for_update().one()
    product.cant += quantity


def remove_stock(session: Session, product_id: int, quantity: int) -> None:
    product = session.query(Product).filter_by(id_prod=product_id).with_for_update().one()
    product.cant -= quantity


def get_stock(session: Session, product_id: int) -> int | None:
    product = session.query(Product).filter_by(id_prod=product_id).with_for_update().first()
    if product is None:
        return None
    return product.cant
