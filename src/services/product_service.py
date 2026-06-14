from decimal import Decimal
from sqlalchemy.orm import Session
from src.models.product import Product


def create_product(session: Session, name: str, cost: Decimal, price: Decimal, cant: int = 0) -> Product:
    product = Product(name=name, cost=cost, price=price, cant=cant)
    session.add(product)
    session.commit()
    return product


def get_product(session: Session, product_id: int) -> Product | None:
    return session.query(Product).filter(Product.idProd == product_id).first()


def get_all_products(session: Session) -> list[Product]:
    return session.query(Product).order_by(Product.idProd).all()


def update_product(session: Session, product_id: int, **kwargs) -> Product | None:
    product = get_product(session, product_id)
    if not product:
        return None
    for key, value in kwargs.items():
        if hasattr(product, key):
            setattr(product, key, value)
    session.commit()
    return product


def delete_product(session: Session, product_id: int) -> bool:
    product = get_product(session, product_id)
    if not product:
        return False
    session.delete(product)
    session.commit()
    return True
