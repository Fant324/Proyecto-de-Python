import pytest
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


@pytest.fixture
def session():
    engine = create_engine(
        "postgresql://postgres:sldptseesc@localhost:5432/stockmanager",
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    s = TestSession()
    try:
        yield s
    finally:
        s.rollback()
        s.close()


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
