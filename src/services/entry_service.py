from datetime import date
from sqlalchemy.orm import Session
from src.models.entry import Entry
from src.services.stock_service import add_stock, get_stock


def register_entry(session: Session, product_id: int, quantity: int, entry_date: date | None = None) -> Entry:
    if product_id <= 0:
        raise ValueError("ID Producto: inválido")
    if quantity <= 0:
        raise ValueError("Cantidad: debe ser mayor a cero")
    entry = Entry(
        id_prod=product_id,
        cant=quantity,
        date=entry_date or date.today(),
    )
    session.add(entry)
    add_stock(session, product_id, quantity)
    session.commit()
    return entry


def get_entries(session: Session) -> list[Entry]:
    return session.query(Entry).order_by(Entry.date.desc(), Entry.idEntry.desc()).all()


def get_entries_by_date_range(session: Session, start_date: date, end_date: date) -> list[Entry]:
    return session.query(Entry).filter(
        Entry.date.between(start_date, end_date),
    ).order_by(Entry.date.desc(), Entry.idEntry.desc()).all()
