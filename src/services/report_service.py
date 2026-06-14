from datetime import date
from decimal import Decimal
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


def get_summary(session: Session, start_date: date, end_date: date):
    revenue_row = session.query(
        func.sum(Sell.revenue).label("total_revenue"),
    ).filter(
        Sell.date.between(start_date, end_date),
    ).first()
    total_revenue = revenue_row.total_revenue or Decimal("0.00")

    cost_row = session.query(
        func.sum(Product.cost * ProdSell.cant).label("total_cost"),
    ).join(ProdSell, ProdSell.id_prod == Product.id_prod
    ).join(Sell, Sell.idSell == ProdSell.idSell
    ).filter(
        Sell.date.between(start_date, end_date),
    ).first()
    total_cost = cost_row.total_cost or Decimal("0.00")

    total_profit = total_revenue - total_cost

    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
    }
