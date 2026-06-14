from decimal import Decimal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QDialog, QMessageBox, QHeaderView,
)
from src.database.session import get_session
from src.services.product_service import (
    create_product, get_all_products, update_product, delete_product,
)


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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Stock", "Costo", "Precio"])
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
                self.table.setItem(i, 0, QTableWidgetItem(str(p.idProd)))
                self.table.setItem(i, 1, QTableWidgetItem(p.name))
                self.table.setItem(i, 2, QTableWidgetItem(str(p.cant)))
                self.table.setItem(i, 3, QTableWidgetItem(str(p.cost)))
                self.table.setItem(i, 4, QTableWidgetItem(str(p.price)))
        finally:
            session.close()

    def _add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            session = get_session()
            try:
                create_product(session, data["name"], data["cost"], data["price"])
                self._load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Producto")
        self.setFixedSize(300, 200)
        self._setup_ui()

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
            "name": self.name_input.text().strip(),
            "cost": Decimal(self.cost_input.text().strip() or "0"),
            "price": Decimal(self.price_input.text().strip() or "0"),
        }
