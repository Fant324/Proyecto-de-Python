from decimal import Decimal
from src.models.user import User
from src.models.product import Product
from src.models.entry import Entry
from src.models.out import Out
from src.models.sell import Sell
from src.models.prod_sell import ProdSell


class TestUserModel:
    def test_create_user(self, session):
        user = User(username="testuser", password="pass", role="admin")
        session.add(user)
        session.flush()
        assert user.id is not None
        assert user.username == "testuser"
        assert user.role == "admin"

    def test_default_role(self, session):
        user = User(username="default_user", password="pass")
        session.add(user)
        session.flush()
        assert user.role == "vendedor"

    def test_username_unique(self, session):
        user1 = User(username="unique_user", password="pass", role="admin")
        session.add(user1)
        session.flush()
        user2 = User(username="unique_user", password="pass2", role="vendedor")
        session.add(user2)
        import pytest
        with pytest.raises(Exception):
            session.flush()


class TestProductModel:
    def test_create_product(self, session):
        product = Product(name="Laptop", cant=10, cost=Decimal("500"), price=Decimal("800"))
        session.add(product)
        session.flush()
        assert product.id_prod is not None
        assert product.name == "Laptop"
        assert product.cant == 10
        assert product.cost == Decimal("500")
        assert product.price == Decimal("800")

    def test_default_stock_zero(self, session):
        product = Product(name="Item", cost=Decimal("1"), price=Decimal("2"))
        session.add(product)
        session.flush()
        assert product.cant == 0


class TestEntryModel:
    def test_create_entry(self, session, sample_product):
        from datetime import date
        entry = Entry(id_prod=sample_product.id_prod, cant=50, date=date.today())
        session.add(entry)
        session.flush()
        assert entry.idEntry is not None
        assert entry.cant == 50


class TestOutModel:
    def test_create_out(self, session, sample_product):
        from datetime import date
        out = Out(id_prod=sample_product.id_prod, cant=10, destination="Cliente A", date=date.today())
        session.add(out)
        session.flush()
        assert out.idOut is not None
        assert out.destination == "Cliente A"


class TestSellModel:
    def test_create_sell(self, session):
        from datetime import date
        sell = Sell(cant=5, revenue=Decimal("125.00"), date=date.today())
        session.add(sell)
        session.flush()
        assert sell.idSell is not None
        assert sell.revenue == Decimal("125.00")


class TestProdSellModel:
    def test_create_prod_sell(self, session, sample_product):
        from datetime import date
        sell = Sell(cant=3, revenue=Decimal("75.00"), date=date.today())
        session.add(sell)
        session.flush()
        ps = ProdSell(id_prod=sample_product.id_prod, idSell=sell.idSell, cant=3)
        session.add(ps)
        session.flush()
        assert ps.id_prod == sample_product.id_prod
        assert ps.idSell == sell.idSell
