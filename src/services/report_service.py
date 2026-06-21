"""Módulo de servicios de reportes - consultas agregadas de ventas, productos y rentabilidad"""

import logging
from datetime import date
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.services.entry_service import get_entries_by_date_range
from src.services.out_service import get_outs_by_date_range
from src.models.sell import Sell
from src.models.product import Product
from src.models.prod_sell import ProdSell
from src.models.v_stock_profit import VStockProfit
from src.models.v_sales_summary import VSalesSummary
from src.models.v_stock_movements import VStockMovement

logger = logging.getLogger(__name__)


def get_entries(session: Session, start_date: date, end_date: date):
    """Obtiene entradas en un rango de fechas delegando al servicio de entradas"""
    return get_entries_by_date_range(session, start_date, end_date)


def get_outs(session: Session, start_date: date, end_date: date):
    """Obtiene salidas en un rango de fechas delegando al servicio de salidas"""
    return get_outs_by_date_range(session, start_date, end_date)


def get_sells(session: Session, start_date: date, end_date: date) -> list[Sell]:
    """Obtiene ventas en un rango de fechas ordenadas por fecha e ID descendentes"""
    return session.query(Sell).filter(
        Sell.date.between(start_date, end_date),
    ).order_by(Sell.date.desc(), Sell.idSell.desc()).all()


def get_sales_by_product(session: Session, start_date: date, end_date: date):
    """Consulta la cantidad total vendida por producto en un rango de fechas, usando JOIN con ProdSell y Sell"""
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


def get_stock_profit(session: Session):
    """Calcula la ganancia esperada por producto usando la vista v_stock_profit, solo productos con stock > 0"""
    return session.query(VStockProfit).filter(
        VStockProfit.stock > 0,
    ).order_by(
        VStockProfit.expected_profit.desc(),
    ).all()


def get_total_sales_by_product(session: Session):
    """Obtiene el resumen total de ventas por producto usando la vista v_sales_summary"""
    return session.query(VSalesSummary).order_by(
        VSalesSummary.total_units_sold.desc(),
    ).all()


def get_stock_movements(session: Session, start_date: date, end_date: date):
    """Obtiene movimientos de stock unificados (entradas y salidas) usando la vista v_stock_movements"""
    return session.query(VStockMovement).filter(
        VStockMovement.date.between(start_date, end_date),
    ).order_by(VStockMovement.date.desc()).all()


def get_summary(session: Session, start_date: date, end_date: date):
    """Genera un resumen de ingresos, costos y ganancia total en un rango de fechas usando consultas agregadas"""
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
