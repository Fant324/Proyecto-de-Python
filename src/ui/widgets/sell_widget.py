"""Módulo del widget de registro de ventas"""

import logging
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QDateEdit,
    QHeaderView, QGroupBox, QSizePolicy,
)
from src.database.session import get_session
from src.services.sell_service import register_sell, get_sells

logger = logging.getLogger(__name__)


class SellWidget(QWidget):
    """Widget que lista las ventas y permite registrar nuevas ventas"""
    def __init__(self, user):
        """Inicializa el widget y carga la lista de ventas"""
        super().__init__()
        self.current_user = user
        self._setup_ui()
        self._load_sells()

    def _setup_ui(self):
        """Construye la interfaz con tabla de ventas y botones"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Registro de Ventas")
        header.setObjectName("header")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nueva Venta")
        self.add_btn.setObjectName("success")
        self.add_btn.clicked.connect(self._add_sell)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self._load_sells)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Unidades", "Ingreso", "Fecha"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        self.setLayout(layout)

    def _load_sells(self):
        """Obtiene las ventas desde la base de datos y las muestra en la tabla"""
        session = get_session()
        try:
            sells = get_sells(session)
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(sells))
            for i, s in enumerate(sells):
                self.table.setItem(i, 0, QTableWidgetItem(str(s.idSell)))
                self.table.setItem(i, 1, QTableWidgetItem(str(s.cant)))
                self.table.setItem(i, 2, QTableWidgetItem(f"${s.revenue}"))
                self.table.setItem(i, 3, QTableWidgetItem(str(s.date)))
            self.table.setSortingEnabled(True)
        finally:
            session.close()

    def _add_sell(self):
        """Abre un diálogo para crear una nueva venta y la registra en la BD"""
        dialog = SellDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                register_sell(session, data["items"], data["date"])
                self._load_sells()
            except ValueError as e:
                logger.exception("Error de validación al registrar venta:")
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                logger.exception("Error inesperado al registrar venta:")
                QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
            finally:
                session.close()


class SellDialog(QDialog):
    """Diálogo para crear una venta con múltiples productos, cantidades y fecha"""

    def __init__(self, parent=None):
        """Inicializa el diálogo con la lista de productos y el selector de fecha"""
        super().__init__(parent)
        self.setWindowTitle("Nueva Venta")
        self.setFixedSize(420, 380)
        self.items = []
        self._setup_ui()

    def _setup_ui(self):
        """Construye el formulario del diálogo con tabla de productos y campos"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Fecha:", self.date_input)
        layout.addLayout(form)

        item_group = QGroupBox("Agregar Producto")
        item_layout = QFormLayout()
        item_layout.setSpacing(8)

        self.prod_input = QLineEdit()
        self.prod_input.setPlaceholderText("ID del producto")
        item_layout.addRow("ID:", self.prod_input)

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        item_layout.addRow("Cant:", self.qty_input)

        add_item_btn = QPushButton("Agregar Producto")
        add_item_btn.setObjectName("success")
        add_item_btn.clicked.connect(self._add_item)
        item_layout.addRow(add_item_btn)

        item_group.setLayout(item_layout)
        layout.addWidget(item_group)

        self.items_list = QTableWidget()
        self.items_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.items_list.setColumnCount(3)
        self.items_list.setHorizontalHeaderLabels(["Producto", "Cantidad", ""])
        self.items_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_list.setAlternatingRowColors(True)
        layout.addWidget(self.items_list, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        save_btn = QPushButton("Guardar Venta")
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

    def _add_item(self):
        """Agrega un producto con su cantidad a la lista de items de la venta"""
        try:
            pid_text = self.prod_input.text().strip()
            if not pid_text:
                raise ValueError("ID Producto: debe ingresar un ID de producto")
            pid = int(pid_text)
            qty_text = self.qty_input.text().strip()
            if not qty_text:
                raise ValueError("Cantidad: debe ingresar una cantidad")
            qty = int(qty_text)
            if qty <= 0:
                raise ValueError("Cantidad: debe ser mayor a cero")
            self.items.append({"product_id": pid, "quantity": qty})
            row = self.items_list.rowCount()
            self.items_list.setSortingEnabled(False)
            self.items_list.setRowCount(row + 1)
            self.items_list.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.items_list.setItem(row, 1, QTableWidgetItem(str(qty)))
            self.items_list.setSortingEnabled(True)
            self.prod_input.clear()
            self.qty_input.clear()
        except ValueError as e:
            logger.exception("Error de validación al agregar producto a venta:")
            QMessageBox.warning(self, "Error", str(e))

    def get_data(self):
        """Valida y retorna los datos de la venta (items y fecha) como diccionario"""
        if not self.items:
            raise ValueError("Productos: debe agregar al menos un producto a la venta")
        return {
            "items": self.items,
            "date": self.date_input.date().toPyDate(),
        }
