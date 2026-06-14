from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QDateEdit, QHeaderView,
)
from PyQt6.QtCore import QDate
from src.database.session import get_session
from src.services.entry_service import register_entry, get_entries
from src.services.product_service import get_all_products


class EntryWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self._setup_ui()
        self._load_entries()

    def _setup_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Registro de Entradas")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nueva Entrada")
        self.add_btn.clicked.connect(self._add_entry)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.clicked.connect(self._load_entries)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Fecha"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _load_entries(self):
        session = get_session()
        try:
            entries = get_entries(session)
            self.table.setRowCount(len(entries))
            for i, e in enumerate(entries):
                self.table.setItem(i, 0, QTableWidgetItem(str(e.idEntry)))
                product = e.idProd
                self.table.setItem(i, 1, QTableWidgetItem(str(product)))
                self.table.setItem(i, 2, QTableWidgetItem(str(e.cant)))
                self.table.setItem(i, 3, QTableWidgetItem(str(e.date)))
        finally:
            session.close()

    def _add_entry(self):
        dialog = EntryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            session = get_session()
            try:
                register_entry(session, data["product_id"], data["cant"], data["date"])
                self._load_entries()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class EntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Entrada")
        self.setFixedSize(300, 200)
        self._setup_ui()

    def _setup_ui(self):
        form = QFormLayout()

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
        return {
            "product_id": int(self.product_input.text().strip()),
            "cant": int(self.cant_input.text().strip()),
            "date": self.date_input.date().toPyDate(),
        }
