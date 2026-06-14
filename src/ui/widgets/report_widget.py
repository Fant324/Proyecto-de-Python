from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QDateEdit,
    QTabWidget, QHeaderView, QMessageBox,
)
from PyQt6.QtCore import QDate
from src.database.session import get_session
from src.services.report_service import get_entries, get_outs, get_sells


class ReportWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Reportes por Fecha")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Desde:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(QLabel("Hasta:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)

        self.filter_btn = QPushButton("Filtrar")
        self.filter_btn.clicked.connect(self._load_reports)
        date_layout.addWidget(self.filter_btn)

        layout.addLayout(date_layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.entry_table = QTableWidget()
        self.entry_table.setColumnCount(4)
        self.entry_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Fecha"])
        self.entry_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.entry_table, "Entradas")

        self.out_table = QTableWidget()
        self.out_table.setColumnCount(5)
        self.out_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Destino", "Fecha"])
        self.out_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.out_table, "Salidas")

        self.sell_table = QTableWidget()
        self.sell_table.setColumnCount(4)
        self.sell_table.setHorizontalHeaderLabels(["ID", "Unidades", "Ingreso", "Fecha"])
        self.sell_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.sell_table, "Ventas")

        self.setLayout(layout)

        self._load_reports()

    def _load_reports(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        session = get_session()
        try:
            entries = get_entries(session, start, end)
            self.entry_table.setRowCount(len(entries))
            for i, e in enumerate(entries):
                self.entry_table.setItem(i, 0, QTableWidgetItem(str(e.idEntry)))
                self.entry_table.setItem(i, 1, QTableWidgetItem(str(e.idProd)))
                self.entry_table.setItem(i, 2, QTableWidgetItem(str(e.cant)))
                self.entry_table.setItem(i, 3, QTableWidgetItem(str(e.date)))

            outs = get_outs(session, start, end)
            self.out_table.setRowCount(len(outs))
            for i, o in enumerate(outs):
                self.out_table.setItem(i, 0, QTableWidgetItem(str(o.idOut)))
                self.out_table.setItem(i, 1, QTableWidgetItem(str(o.idProd)))
                self.out_table.setItem(i, 2, QTableWidgetItem(str(o.cant)))
                self.out_table.setItem(i, 3, QTableWidgetItem(o.destination))
                self.out_table.setItem(i, 4, QTableWidgetItem(str(o.date)))

            sells = get_sells(session, start, end)
            self.sell_table.setRowCount(len(sells))
            for i, s in enumerate(sells):
                self.sell_table.setItem(i, 0, QTableWidgetItem(str(s.idSell)))
                self.sell_table.setItem(i, 1, QTableWidgetItem(str(s.cant)))
                self.sell_table.setItem(i, 2, QTableWidgetItem(f"${s.revenue}"))
                self.sell_table.setItem(i, 3, QTableWidgetItem(str(s.date)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()
