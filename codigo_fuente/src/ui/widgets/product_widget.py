"""Módulo del widget de gestión de productos"""

import logging
from decimal import Decimal
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QHeaderView,
    QSizePolicy,
)
from src.database.session import get_session
from src.services.product_service import (
    create_product, get_all_products, update_product, delete_product,
)

logger = logging.getLogger(__name__)


def _to_decimal(value: str, field: str) -> Decimal:
    """Convierte una cadena a Decimal limpiando formato, útil para costo/precio"""
    value = value.strip().replace(",", ".")
    value = re.sub(r"[^\d.\-]", "", value)
    if not value or value in (".", "-"):
        raise ValueError(f"{field}: ingrese un número válido")
    try:
        return Decimal(value)
    except Exception:
        raise ValueError(f"{field}: ingrese un número válido")


class ProductWidget(QWidget):
    """Widget que lista los productos y permite crear, editar y eliminar productos"""

    def __init__(self, user):
        """Inicializa el widget y carga la lista de productos"""
        super().__init__()
        self.current_user = user
        self._setup_ui()
        self._load_products()

    def _setup_ui(self):
        """Construye la interfaz con tabla de productos y botones"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Gestión de Productos")
        header.setObjectName("header")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nuevo Producto")
        self.add_btn.setObjectName("success")
        self.add_btn.clicked.connect(self._add_product)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self._load_products)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Stock", "Costo", "Precio", "Editar", "Eliminar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        self.setLayout(layout)

    def _load_products(self):
        """Obtiene los productos desde la base de datos y los muestra en la tabla"""
        session = get_session()
        try:
            products = get_all_products(session)
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(products))
            for i, p in enumerate(products):
                self.table.setItem(i, 0, QTableWidgetItem(str(p.id_prod)))
                self.table.setItem(i, 1, QTableWidgetItem(p.name))
                self.table.setItem(i, 2, QTableWidgetItem(str(p.cant)))
                self.table.setItem(i, 3, QTableWidgetItem(str(p.cost)))
                self.table.setItem(i, 4, QTableWidgetItem(str(p.price)))

                edit_btn = QPushButton("Editar")
                edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                edit_btn.clicked.connect(lambda checked, pid=p.id_prod: self._edit_product(pid))
                self.table.setCellWidget(i, 5, edit_btn)

                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("danger")
                delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                delete_btn.clicked.connect(lambda checked, pid=p.id_prod: self._delete_product(pid))
                self.table.setCellWidget(i, 6, delete_btn)
            self.table.setSortingEnabled(True)
        finally:
            session.close()

    def _add_product(self):
        """Abre un diálogo para crear un nuevo producto y lo registra en la BD"""
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                create_product(session, data["name"], data["cost"], data["price"], data.get("cant", 0))
                self._load_products()
            except Exception as e:
                logger.exception("Error inesperado al crear producto:")
                QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
            finally:
                session.close()

    def _edit_product(self, product_id: int):
        """Abre un diálogo para editar un producto existente y guarda los cambios"""
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
            logger.exception("Error inesperado al editar producto:")
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
        finally:
            session.close()

    def _delete_product(self, product_id: int):
        """Elimina un producto tras confirmación del usuario"""
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
                logger.exception("Error inesperado al eliminar producto:")
                QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
            finally:
                session.close()


class ProductDialog(QDialog):
    """Diálogo para crear o editar un producto (nombre, costo, precio, stock)"""
    def __init__(self, parent=None, product=None):
        """Inicializa el diálogo; si recibe un producto, carga sus datos para edición"""
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Editar Producto" if product else "Nuevo Producto")
        self.setFixedSize(320, 260)
        self._setup_ui()
        if product:
            self.name_input.setText(product.name)
            self.cost_input.setText(str(product.cost))
            self.price_input.setText(str(product.price))
            self.cant_input.setText(str(product.cant))

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

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

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("success")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("danger")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        """Valida y retorna los datos del formulario como diccionario"""
        name = self.name_input.text().strip()
        if not name:
            raise ValueError("Nombre: el nombre del producto no puede estar vacío")
        cost = _to_decimal(self.cost_input.text(), "Costo")
        if cost <= 0:
            raise ValueError("Costo: debe ser un número positivo")
        price = _to_decimal(self.price_input.text(), "Precio")
        if price <= 0:
            raise ValueError("Precio: debe ser un número positivo")
        return {
            "name": name,
            "cost": cost,
            "price": price,
            "cant": int(self.cant_input.text().strip() or "0"),
        }
