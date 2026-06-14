from sqlalchemy import text
from sqlalchemy.orm import Session


def add_stock(session: Session, product_id: int, quantity: int) -> None:
    session.execute(
        text('UPDATE product SET cant = cant + :qty WHERE "idProd" = :pid'),
        {"qty": quantity, "pid": product_id},
    )


def remove_stock(session: Session, product_id: int, quantity: int) -> None:
    session.execute(
        text('UPDATE product SET cant = cant - :qty WHERE "idProd" = :pid'),
        {"qty": quantity, "pid": product_id},
    )


def get_stock(session: Session, product_id: int) -> int | None:
    result = session.execute(
        text('SELECT cant FROM product WHERE "idProd" = :pid FOR UPDATE'),
        {"pid": product_id},
    ).scalar()
    return result
