from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from src.models.sell import Sell
from src.models.prod_sell import ProdSell
from src.services.stock_service import get_stock, remove_stock
from src.services.product_service import get_product


def register_sell(
    session: Session,
    items: list[dict],
    sell_date: date | None = None,
) -> Sell:
    if not items:
        raise ValueError("Productos: debe incluir al menos un producto en la venta")
    total_units = 0
    total_revenue = Decimal("0.00")

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        product = get_product(session, product_id)
        if not product:
            raise ValueError(f"Producto ID {product_id} no existe")

        current_stock = get_stock(session, product_id)
        if current_stock is None or current_stock < quantity:
            raise ValueError(
                f"Stock insuficiente para '{product.name}': "
                f"disponible {current_stock}, requerido {quantity}"
            )

        total_units += quantity
        total_revenue += product.price * quantity

    sell = Sell(
        cant=total_units,
        revenue=total_revenue,
        date=sell_date or date.today(),
    )
    session.add(sell)
    session.flush()

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        prod_sell = ProdSell(
            id_prod=product_id,
            idSell=sell.idSell,
            cant=quantity,
        )
        session.add(prod_sell)
        remove_stock(session, product_id, quantity)

    session.commit()
    return sell


def get_sells(session: Session) -> list[Sell]:
    return session.query(Sell).order_by(Sell.date.desc(), Sell.idSell.desc()).all()


def get_sells_by_date_range(session: Session, start_date: date, end_date: date) -> list[Sell]:
    return session.query(Sell).filter(
        Sell.date.between(start_date, end_date),
    ).order_by(Sell.date.desc(), Sell.idSell.desc()).all()


def get_prod_sells_by_sell(session: Session, sell_id: int) -> list[ProdSell]:
    return session.query(ProdSell).filter(ProdSell.idSell == sell_id).all()
