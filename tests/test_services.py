from decimal import Decimal
from datetime import date
import pytest
from src.services.auth_service import authenticate_user, verify_role, require_admin
from src.services.user_service import create_user, get_user, get_all_users, delete_user
from src.services.product_service import create_product, get_product, get_all_products, delete_product
from src.services.entry_service import register_entry, get_entries_by_date_range
from src.services.out_service import register_out, get_outs_by_date_range
from src.services.sell_service import register_sell, get_sells_by_date_range
from src.services.report_service import get_entries, get_outs, get_sells
from src.models.user import User


class TestAuthService:
    def test_authenticate_success(self, session, admin_user):
        user = authenticate_user(session, "test_admin", "1234")
        assert user is not None
        assert user.username == "test_admin"

    def test_authenticate_fail_wrong_password(self, session, admin_user):
        user = authenticate_user(session, "test_admin", "wrong")
        assert user is None

    def test_authenticate_fail_nonexistent(self, session):
        user = authenticate_user(session, "no_exist", "pass")
        assert user is None

    def test_verify_role_admin(self, session, admin_user):
        assert verify_role(admin_user, "admin") is True
        assert verify_role(admin_user, "vendedor") is False

    def test_require_admin_allows_admin(self, session, admin_user):
        require_admin(admin_user)

    def test_require_admin_denies_seller(self, session, seller_user):
        with pytest.raises(PermissionError):
            require_admin(seller_user)


class TestUserService:
    def test_create_user(self, session):
        user = create_user(session, "new_user", "pass", "vendedor")
        assert user.id is not None
        assert user.username == "new_user"
        assert user.role == "vendedor"

    def test_get_user_by_id(self, session, admin_user):
        found = get_user(session, admin_user.id)
        assert found is not None
        assert found.username == "test_admin"

    def test_get_all_users(self, session, admin_user, seller_user):
        users = get_all_users(session)
        assert len(users) >= 2

    def test_delete_user(self, session):
        user = create_user(session, "to_delete", "pass", "vendedor")
        admin = create_user(session, "del_test_admin", "pass", "admin")
        result = delete_user(session, user.id, admin)
        assert result is True
        assert get_user(session, user.id) is None

    def test_delete_last_admin_raises(self, session):
        admin_count_before = session.query(User).filter(User.role == "admin").count()
        admin = create_user(session, "sole_admin_test", "pass", "admin")
        if admin_count_before == 0:
            with pytest.raises(ValueError, match="único administrador"):
                delete_user(session, admin.id, admin)
        else:
            delete_user(session, admin.id, admin)
            assert get_user(session, admin.id) is None


class TestProductService:
    def test_create_product(self, session):
        product = create_product(session, "Monitor", Decimal("150"), Decimal("300"), 20)
        assert product.idProd is not None
        assert product.name == "Monitor"
        assert product.cant == 20

    def test_get_product(self, session, sample_product):
        found = get_product(session, sample_product.idProd)
        assert found is not None
        assert found.name == "Test Producto"

    def test_get_all_products(self, session, sample_product):
        products = get_all_products(session)
        assert len(products) >= 1

    def test_delete_product(self, session, sample_product):
        result = delete_product(session, sample_product.idProd)
        assert result is True
        assert get_product(session, sample_product.idProd) is None


class TestEntryService:
    def test_register_entry_increases_stock(self, session, sample_product):
        initial = sample_product.cant
        entry = register_entry(session, sample_product.idProd, 50)
        assert entry.idEntry is not None
        assert entry.cant == 50
        session.flush()
        session.refresh(sample_product)
        assert sample_product.cant == initial + 50

    def test_get_entries_by_date(self, session, sample_product):
        today = date.today()
        register_entry(session, sample_product.idProd, 10, today)
        entries = get_entries_by_date_range(session, today, today)
        assert len(entries) >= 1


class TestOutService:
    def test_register_out_decreases_stock(self, session, sample_product):
        initial = sample_product.cant
        out = register_out(session, sample_product.idProd, 30, "Destino Test")
        assert out.idOut is not None
        session.flush()
        session.refresh(sample_product)
        assert sample_product.cant == initial - 30

    def test_register_out_insufficient_stock(self, session, sample_product):
        with pytest.raises(ValueError, match="Stock insuficiente"):
            register_out(session, sample_product.idProd, 9999, "Test")

    def test_get_outs_by_date(self, session, sample_product):
        today = date.today()
        register_out(session, sample_product.idProd, 5, "Destino", today)
        outs = get_outs_by_date_range(session, today, today)
        assert len(outs) >= 1


class TestSellService:
    def test_register_sell_calculates_revenue(self, session, sample_product):
        sell = register_sell(session, [{"product_id": sample_product.idProd, "quantity": 4}])
        assert sell.cant == 4
        assert sell.revenue == Decimal("100.00")

    def test_register_sell_decreases_stock(self, session, sample_product):
        initial = sample_product.cant
        register_sell(session, [{"product_id": sample_product.idProd, "quantity": 5}])
        session.flush()
        session.refresh(sample_product)
        assert sample_product.cant == initial - 5

    def test_register_sell_multiple_products(self, session):
        p1 = create_product(session, "Prod A", Decimal("10"), Decimal("20"), 50)
        p2 = create_product(session, "Prod B", Decimal("15"), Decimal("30"), 50)
        sell = register_sell(session, [
            {"product_id": p1.idProd, "quantity": 3},
            {"product_id": p2.idProd, "quantity": 2},
        ])
        assert sell.cant == 5
        assert sell.revenue == Decimal("120.00")

    def test_register_sell_insufficient_stock(self, session, sample_product):
        with pytest.raises(ValueError, match="Stock insuficiente"):
            register_sell(session, [{"product_id": sample_product.idProd, "quantity": 9999}])

    def test_get_sells_by_date(self, session, sample_product):
        today = date.today()
        register_sell(session, [{"product_id": sample_product.idProd, "quantity": 1}])
        sells = get_sells_by_date_range(session, today, today)
        assert len(sells) >= 1


class TestReportService:
    def test_get_entries_report(self, session, sample_product):
        today = date.today()
        register_entry(session, sample_product.idProd, 25, today)
        entries = get_entries(session, today, today)
        assert len(entries) >= 1

    def test_get_outs_report(self, session, sample_product):
        today = date.today()
        register_out(session, sample_product.idProd, 8, "Reporte Test", today)
        outs = get_outs(session, today, today)
        assert len(outs) >= 1

    def test_get_sells_report(self, session, sample_product):
        today = date.today()
        register_sell(session, [{"product_id": sample_product.idProd, "quantity": 2}])
        sells = get_sells(session, today, today)
        assert len(sells) >= 1
