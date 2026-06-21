import pytest
from pathlib import Path
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.database.base import Base
from src.models.user import User
from src.models.product import Product
from src.models.entry import Entry
from src.models.out import Out
from src.models.sell import Sell
from src.models.prod_sell import ProdSell

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"

SQL_FILES = ["tables.sql", "views.sql", "triggers.sql"]


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        "postgresql://postgres:sldptseesc@localhost:5432/stockmanager",
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    for sql_file in SQL_FILES:
        filepath = SQL_DIR / sql_file
        if filepath.exists():
            with open(filepath, encoding="utf-8") as f:
                with engine.begin() as conn:
                    conn.execute(text(f.read()))
    yield engine
    engine.dispose()


@pytest.fixture
def session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def admin_user(session: Session) -> User:
    from src.services.auth_service import hash_password
    user = User(username="test_admin", password=hash_password("1234"), role="admin")
    session.add(user)
    session.flush()
    return user


@pytest.fixture
def seller_user(session: Session) -> User:
    from src.services.auth_service import hash_password
    user = User(username="test_seller", password=hash_password("1234"), role="vendedor")
    session.add(user)
    session.flush()
    return user


@pytest.fixture
def sample_product(session: Session) -> Product:
    product = Product(name="Test Producto", cant=100, cost=Decimal("10.50"), price=Decimal("25.00"))
    session.add(product)
    session.flush()
    return product
