from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QDateEdit, QHeaderView,
)
from PyQt6.QtCore import QDate
from src.database.session import get_session
from src.services.out_service import register_out, get_outs


class OutWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self._setup_ui()
        self._load_outs()

    def _setup_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Registro de Salidas")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nueva Salida")
        self.add_btn.clicked.connect(self._add_out)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.clicked.connect(self._load_outs)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Destino", "Fecha"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _load_outs(self):
        session = get_session()
        try:
            outs = get_outs(session)
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
        finally:
            session.close()

    def _add_out(self):
        dialog = OutDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                register_out(session, data["product_id"], data["cant"], data["destination"], data["date"])
                self._load_outs()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class OutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Salida")
        self.setFixedSize(300, 250)
        self._setup_ui()

    def _setup_ui(self):
        form = QFormLayout()

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
        product_text = self.product_input.text().strip()
        if not product_text:
            raise ValueError("Debe ingresar un ID de producto")
        product_id = int(product_text)
        cant = int(self.cant_input.text().strip())
        if cant <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        destination = self.dest_input.text().strip()
        if not destination:
            raise ValueError("El destino no puede estar vacío")
        return {
            "product_id": product_id,
            "cant": cant,
            "destination": destination,
            "date": self.date_input.date().toPyDate(),
        }
