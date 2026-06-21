"""Módulo de servicios de ventas - registro de ventas, cálculo de ingresos y descuento de stock"""

import logging
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from src.models.product import Product
from src.models.sell import Sell
from src.models.prod_sell import ProdSell

logger = logging.getLogger(__name__)


def register_sell(
    session: Session,
    items: list[dict],
    sell_date: date | None = None,
) -> Sell:
    """Registra una venta validando stock de cada producto, calcula ingresos totales, descuenta stock y persiste"""
    if not items:
        raise ValueError("Productos: debe incluir al menos un producto en la venta")
    total_units = 0
    total_revenue = Decimal("0.00")

    products_locked = []
    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        product = session.query(Product).filter_by(id_prod=product_id).with_for_update().first()
        if not product:
            raise ValueError(f"Producto ID {product_id} no existe")
        if product.cant < quantity:
            raise ValueError(
                f"Stock insuficiente para '{product.name}': "
                f"disponible {product.cant}, requerido {quantity}"
            )

        total_units += quantity
        total_revenue += product.price * quantity
        products_locked.append((product, quantity))

    sell = Sell(
        cant=total_units,
        revenue=total_revenue,
        date=sell_date or date.today(),
    )
    session.add(sell)
    session.flush()

    for product, quantity in products_locked:
        prod_sell = ProdSell(
            id_prod=product.id_prod,
            idSell=sell.idSell,
            cant=quantity,
        )
        session.add(prod_sell)
        product.cant -= quantity

    session.commit()
    return sell


def get_sells(session: Session) -> list[Sell]:
    """Obtiene todas las ventas ordenadas por fecha descendente y luego por ID"""
    return session.query(Sell).order_by(Sell.date.desc(), Sell.idSell.desc()).all()


def get_sells_by_date_range(session: Session, start_date: date, end_date: date) -> list[Sell]:
    """Filtra ventas dentro de un rango de fechas, ordenadas por fecha e ID descendentes"""
    return session.query(Sell).filter(
        Sell.date.between(start_date, end_date),
    ).order_by(Sell.date.desc(), Sell.idSell.desc()).all()


def get_prod_sells_by_sell(session: Session, sell_id: int) -> list[ProdSell]:
    """Obtiene los productos asociados a una venta específica por el ID de la venta"""
    return session.query(ProdSell).filter(ProdSell.idSell == sell_id).all()
