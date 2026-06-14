from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.services.entry_service import get_entries_by_date_range
from src.services.out_service import get_outs_by_date_range
from src.models.sell import Sell
from src.models.product import Product
from src.models.prod_sell import ProdSell


def get_entries(session: Session, start_date: date, end_date: date):
    return get_entries_by_date_range(session, start_date, end_date)


def get_outs(session: Session, start_date: date, end_date: date):
    return get_outs_by_date_range(session, start_date, end_date)


def get_sells(session: Session, start_date: date, end_date: date) -> list[Sell]:
    return session.query(Sell).filter(
        Sell.date.between(start_date, end_date),
    ).order_by(Sell.date.desc(), Sell.idSell.desc()).all()


def get_sales_by_product(session: Session, start_date: date, end_date: date):
    return session.query(
        Product.id_prod,
        Product.name,
        func.sum(ProdSell.cant).label("total_sold"),
    ).join(ProdSell, ProdSell.id_prod == Product.id_prod
    ).join(Sell, Sell.idSell == ProdSell.idSell
    ).filter(
        Sell.date.between(start_date, end_date),
    ).group_by(
        Product.id_prod, Product.name,
    ).order_by(
        func.sum(ProdSell.cant).desc(),
    ).all()
