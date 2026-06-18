"""Módulo del widget de registro de entradas de inventario"""

import logging
from datetime import date
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QDateEdit, QHeaderView,
    QSizePolicy,
)
from src.database.session import get_session
from src.services.entry_service import register_entry, get_entries
from src.services.product_service import get_all_products

logger = logging.getLogger(__name__)


class EntryWidget(QWidget):
    """Widget que lista las entradas y permite agregar nuevas entradas al inventario"""
    def __init__(self, user):
        """Inicializa el widget y carga la lista de entradas"""
        super().__init__()
        self.current_user = user
        self._setup_ui()
        self._load_entries()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Registro de Entradas")
        header.setObjectName("header")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nueva Entrada")
        self.add_btn.setObjectName("success")
        self.add_btn.clicked.connect(self._add_entry)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self._load_entries)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Fecha"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        self.setLayout(layout)

    def _load_entries(self):
        """Obtiene las entradas desde la base de datos y las muestra en la tabla"""
        session = get_session()
        try:
            entries = get_entries(session)
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(entries))
            for i, e in enumerate(entries):
                self.table.setItem(i, 0, QTableWidgetItem(str(e.idEntry)))
                from src.models.product import Product
                product = session.get(Product, e.id_prod)
                name = product.name if product else str(e.id_prod)
                self.table.setItem(i, 1, QTableWidgetItem(name))
                self.table.setItem(i, 2, QTableWidgetItem(str(e.cant)))
                self.table.setItem(i, 3, QTableWidgetItem(str(e.date)))
            self.table.setSortingEnabled(True)
        finally:
            session.close()

    def _add_entry(self):
        """Abre un diálogo para crear una nueva entrada y la registra en la BD"""
        dialog = EntryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                register_entry(session, data["product_id"], data["cant"], data["date"])
                self._load_entries()
            except Exception as e:
                logger.exception("Error inesperado al registrar entrada:")
                QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
            finally:
                session.close()


class EntryDialog(QDialog):
    """Diálogo para ingresar los datos de una nueva entrada (producto, cantidad, fecha)"""

    def __init__(self, parent=None):
        """Inicializa el diálogo con campos para producto, cantidad y fecha"""
        super().__init__(parent)
        self.setWindowTitle("Nueva Entrada")
        self.setFixedSize(320, 220)
        self._setup_ui()

    def _setup_ui(self):
        """Construye el formulario del diálogo"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("ID del producto")
        form.addRow("ID Producto:", self.product_input)

        self.cant_input = QLineEdit()
        self.cant_input.setPlaceholderText("Cantidad")
        form.addRow("Cantidad:", self.cant_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Fecha:", self.date_input)

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
        product_text = self.product_input.text().strip()
        if not product_text:
            raise ValueError("ID Producto: debe ingresar un ID de producto")
        try:
            product_id = int(product_text)
        except ValueError:
            raise ValueError("ID Producto: debe ser un número")
        try:
            cant = int(self.cant_input.text().strip())
        except ValueError:
            raise ValueError("Cantidad: debe ser un número entero")
        if cant <= 0:
            raise ValueError("Cantidad: debe ser mayor a cero")
        return {
            "product_id": product_id,
            "cant": cant,
            "date": self.date_input.date().toPyDate(),
        }
