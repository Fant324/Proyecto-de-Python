"""Módulo de servicios de salidas de inventario - registro y consulta de salidas de productos"""

import logging
from datetime import date
from sqlalchemy.orm import Session
from src.models.out import Out
from src.services.stock_service import remove_stock, get_stock

logger = logging.getLogger(__name__)


def register_out(session: Session, product_id: int, quantity: int, destination: str, out_date: date | None = None) -> Out:
    """Registra una salida validando stock suficiente, destino y datos; actualiza el stock y persiste"""
    if product_id <= 0:
        raise ValueError("ID Producto: inválido")
    if quantity <= 0:
        raise ValueError("Cantidad: debe ser mayor a cero")
    if not destination:
        raise ValueError("Destino: no puede estar vacío")
    current_stock = get_stock(session, product_id)
    if current_stock is None:
        raise ValueError("El producto no existe")
    if current_stock < quantity:
        raise ValueError(f"Stock insuficiente: disponible {current_stock}, requerido {quantity}")

    out = Out(
        id_prod=product_id,
        cant=quantity,
        destination=destination,
        date=out_date or date.today(),
    )
    session.add(out)
    remove_stock(session, product_id, quantity)
    session.commit()
    return out


def get_outs(session: Session) -> list[Out]:
    """Obtiene todas las salidas ordenadas por fecha descendente y luego por ID"""
    return session.query(Out).order_by(Out.date.desc(), Out.idOut.desc()).all()


def get_outs_by_date_range(session: Session, start_date: date, end_date: date) -> list[Out]:
    """Filtra salidas dentro de un rango de fechas, ordenadas por fecha e ID descendentes"""
    return session.query(Out).filter(
        Out.date.between(start_date, end_date),
    ).order_by(Out.date.desc(), Out.idOut.desc()).all()
