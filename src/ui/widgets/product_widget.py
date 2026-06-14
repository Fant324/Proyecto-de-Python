from decimal import Decimal
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QHeaderView,
)
from src.database.session import get_session
from src.services.product_service import (
    create_product, get_all_products, update_product, delete_product,
)


def _to_decimal(value: str) -> Decimal:
    value = value.strip().replace(",", ".")
    value = re.sub(r"[^\d.\-]", "", value)
    if not value or value in (".", "-"):
        raise ValueError("Ingrese un número válido")
    try:
        return Decimal(value)
    except Exception:
        raise ValueError("Ingrese un número válido")


class ProductWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self._setup_ui()
        self._load_products()

    def _setup_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Gestión de Productos")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nuevo Producto")
        self.add_btn.clicked.connect(self._add_product)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.clicked.connect(self._load_products)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Stock", "Costo", "Precio", "Editar", "Eliminar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _load_products(self):
        session = get_session()
        try:
            products = get_all_products(session)
            self.table.setRowCount(len(products))
            for i, p in enumerate(products):
                self.table.setItem(i, 0, QTableWidgetItem(str(p.id_prod)))
                self.table.setItem(i, 1, QTableWidgetItem(p.name))
                self.table.setItem(i, 2, QTableWidgetItem(str(p.cant)))
                self.table.setItem(i, 3, QTableWidgetItem(str(p.cost)))
                self.table.setItem(i, 4, QTableWidgetItem(str(p.price)))

                edit_btn = QPushButton("Editar")
                edit_btn.clicked.connect(lambda checked, pid=p.id_prod: self._edit_product(pid))
                self.table.setCellWidget(i, 5, edit_btn)

                delete_btn = QPushButton("Eliminar")
                delete_btn.clicked.connect(lambda checked, pid=p.id_prod: self._delete_product(pid))
                self.table.setCellWidget(i, 6, delete_btn)
        finally:
            session.close()

    def _add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                create_product(session, data["name"], data["cost"], data["price"], data.get("cant", 0))
                self._load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()

    def _edit_product(self, product_id: int):
        session = get_session()
        try:
            from src.services.product_service import get_product
            product = get_product(session, product_id)
            if not product:
                QMessageBox.warning(self, "Error", "Producto no encontrado")
                return
            dialog = ProductDialog(self, product)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                update_product(session, product_id,
                               name=data["name"],
                               cost=data["cost"],
                               price=data["price"],
                               cant=data.get("cant", product.cant))
                self._load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()

    def _delete_product(self, product_id: int):
        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar este producto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                delete_product(session, product_id)
                self._load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Editar Producto" if product else "Nuevo Producto")
        self.setFixedSize(300, 250)
        self._setup_ui()
        if product:
            self.name_input.setText(product.name)
            self.cost_input.setText(str(product.cost))
            self.price_input.setText(str(product.price))
            self.cant_input.setText(str(product.cant))

    def _setup_ui(self):
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        form.addRow("Nombre:", self.name_input)

        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        form.addRow("Costo:", self.cost_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        form.addRow("Precio:", self.price_input)

        self.cant_input = QLineEdit()
        self.cant_input.setPlaceholderText("Stock inicial (opcional)")
        form.addRow("Stock:", self.cant_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        form.addRow(btn_layout)
        self.setLayout(form)

    def get_data(self):
        name = self.name_input.text().strip()
        if not name:
            raise ValueError("El nombre del producto no puede estar vacío")
        cost = _to_decimal(self.cost_input.text())
        if cost <= 0:
            raise ValueError("El costo debe ser un número positivo")
        price = _to_decimal(self.price_input.text())
        if price <= 0:
            raise ValueError("El precio debe ser un número positivo")
        return {
            "name": name,
            "cost": cost,
            "price": price,
            "cant": int(self.cant_input.text().strip() or "0"),
        }
