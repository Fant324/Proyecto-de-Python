"""Módulo del widget de registro de salidas de inventario"""

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
from src.ui.base_dialog import BaseDialog
from src.services.auth_service import require_role
from src.services.out_service import register_out, get_outs

logger = logging.getLogger(__name__)


class OutWidget(QWidget):
    """Widget que lista las salidas y permite registrar nuevas salidas de inventario"""
    def __init__(self, user):
        """Inicializa el widget y carga la lista de salidas"""
        super().__init__()
        self.current_user = user
        require_role(self.current_user, "admin", "almacen")
        self._setup_ui()
        self._load_outs()

    def _setup_ui(self):
        """Construye la interfaz con tabla de salidas y botones"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Registro de Salidas")
        header.setObjectName("header")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nueva Salida")
        self.add_btn.setObjectName("success")
        self.add_btn.clicked.connect(self._add_out)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self._load_outs)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Destino", "Fecha"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        self.setLayout(layout)

    def _load_outs(self):
        """Obtiene las salidas desde la base de datos y las muestra en la tabla"""
        session = get_session()
        try:
            outs = get_outs(session)
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(outs))
            for i, o in enumerate(outs):
                self.table.setItem(i, 0, QTableWidgetItem(str(o.idOut)))
                from src.models.product import Product
                product = session.get(Product, o.id_prod)
                name = product.name if product else str(o.id_prod)
                self.table.setItem(i, 1, QTableWidgetItem(name))
                self.table.setItem(i, 2, QTableWidgetItem(str(o.cant)))
                self.table.setItem(i, 3, QTableWidgetItem(o.destination))
                self.table.setItem(i, 4, QTableWidgetItem(str(o.date)))
            self.table.setSortingEnabled(True)
        finally:
            session.close()

    def _add_out(self):
        """Abre un diálogo para crear una nueva salida y la registra en la BD"""
        dialog = OutDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                register_out(session, data["product_id"], data["cant"], data["destination"], data["date"])
                self._load_outs()
            except ValueError as e:
                logger.exception("Error de validación al registrar salida:")
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                logger.exception("Error inesperado al registrar salida:")
                QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
            finally:
                session.close()


class OutDialog(BaseDialog):
    """Diálogo para ingresar los datos de una nueva salida (producto, cantidad, destino, fecha)"""

    def __init__(self, parent=None):
        """Inicializa el diálogo con campos para producto, cantidad, destino y fecha"""
        super().__init__(parent, "Nueva Salida")
        self.setFixedSize(320, 260)
        self._setup_ui()

    def _setup_ui(self):
        """Construye el formulario del diálogo"""
        form = QFormLayout()
        form.setSpacing(8)

        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("ID del producto")
        form.addRow("ID Producto:", self.product_input)

        self.cant_input = QLineEdit()
        self.cant_input.setPlaceholderText("Cantidad")
        form.addRow("Cantidad:", self.cant_input)

        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Destino")
        form.addRow("Destino:", self.dest_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow("Fecha:", self.date_input)

        self.content_layout.addLayout(form)

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
        self.content_layout.addLayout(btn_layout)

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
        destination = self.dest_input.text().strip()
        if not destination:
            raise ValueError("Destino: no puede estar vacío")
        return {
            "product_id": product_id,
            "cant": cant,
            "destination": destination,
            "date": self.date_input.date().toPyDate(),
        }
