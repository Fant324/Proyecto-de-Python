"""Módulo del widget de reportes por fecha con exportación CSV y conversión de moneda"""

import logging
import csv
import json
from pathlib import Path
from datetime import date
from decimal import Decimal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QDateEdit,
    QTabWidget, QHeaderView, QMessageBox, QFileDialog,
    QCheckBox, QDoubleSpinBox, QSizePolicy,
)
from PyQt6.QtCore import QDate
from src.database.session import get_session
from src.services.report_service import get_entries, get_outs, get_sells, get_sales_by_product, get_stock_profit, get_summary

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "conversion_config.json"


class ReportWidget(QWidget):
    """Widget que muestra reportes de entradas, salidas, ventas, productos y resumen con filtro por fechas"""
    def __init__(self, user):
        """Inicializa el widget y configura la interfaz"""
        super().__init__()
        self.current_user = user
        self._setup_ui()

    def _load_rate(self):
        """Carga la tasa de conversión desde el archivo de configuración"""
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
                return float(data.get("rate", 24.0))
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            return 24.0

    def _save_rate(self, rate):
        """Guarda la tasa de conversión en el archivo de configuración"""
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"rate": rate}, f)
        except OSError:
            pass

    def _setup_ui(self):
        """Construye la interfaz con pestañas de reportes, filtros de fecha y opciones de exportación"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QLabel("Reportes por Fecha")
        header.setObjectName("header")
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

        self.export_btn = QPushButton("Exportar CSV")
        self.export_btn.clicked.connect(self._export_csv)
        date_layout.addWidget(self.export_btn)

        self.convert_cb = QCheckBox("Convertir a CUP")
        self.convert_cb.toggled.connect(self._on_toggle_conversion)
        date_layout.addWidget(self.convert_cb)

        saved_rate = self._load_rate()
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setDecimals(4)
        self.rate_input.setRange(0.0001, 999999.0)
        self.rate_input.setValue(saved_rate)
        self.rate_input.setPrefix("Tasa: ")
        self.rate_input.setEnabled(False)
        self.rate_input.valueChanged.connect(lambda v: self._save_rate(v))
        date_layout.addWidget(self.rate_input)

        layout.addLayout(date_layout)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.tabs, 1)

        self.entry_table = QTableWidget()
        self.entry_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.entry_table.setColumnCount(4)
        self.entry_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Fecha"])
        self.entry_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.entry_table.setAlternatingRowColors(True)
        self.entry_table.setSortingEnabled(True)
        self.tabs.addTab(self.entry_table, "Entradas")

        self.out_table = QTableWidget()
        self.out_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.out_table.setColumnCount(5)
        self.out_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Destino", "Fecha"])
        self.out_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.out_table.setAlternatingRowColors(True)
        self.out_table.setSortingEnabled(True)
        self.tabs.addTab(self.out_table, "Salidas")

        self.sell_table = QTableWidget()
        self.sell_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sell_table.setColumnCount(4)
        self.sell_table.setHorizontalHeaderLabels(["ID", "Unidades", "Ingreso", "Fecha"])
        self.sell_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sell_table.setAlternatingRowColors(True)
        self.sell_table.setSortingEnabled(True)
        self.tabs.addTab(self.sell_table, "Ventas")

        self.sales_by_product_table = QTableWidget()
        self.sales_by_product_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sales_by_product_table.setColumnCount(2)
        self.sales_by_product_table.setHorizontalHeaderLabels(["Producto", "Cantidad Vendida"])
        self.sales_by_product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sales_by_product_table.setAlternatingRowColors(True)
        self.sales_by_product_table.setSortingEnabled(True)
        self.tabs.addTab(self.sales_by_product_table, "Ventas por Producto")

        self.product_table = QTableWidget()
        self.product_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["Producto", "Stock", "Precio", "Costo", "Ganancia Esp."])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setSortingEnabled(True)
        self.tabs.addTab(self.product_table, "Productos")

        self.summary_table = QTableWidget()
        self.summary_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setRowCount(3)
        self.tabs.addTab(self.summary_table, "Resumen")

        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.setLayout(layout)

        self._on_tab_changed(self.tabs.currentIndex())
        self._load_reports()
        self._update_sell_columns(False)

    def _on_tab_changed(self, index):
        """Muestra u oculta los controles de conversión según la pestaña activa"""
        show = index in (2, 4, 5)
        self.convert_cb.setVisible(show)
        self.rate_input.setVisible(show)

    def _on_toggle_conversion(self, enabled):
        """Activa o desactiva la conversión de moneda y recarga los reportes"""
        self.rate_input.setEnabled(enabled)
        self._update_sell_columns(enabled)
        self._load_reports()

    def _update_sell_columns(self, enabled):
        """Ajusta las columnas de las tablas según si la conversión está activa o no"""
        if enabled:
            self.sell_table.setColumnCount(5)
            self.sell_table.setHorizontalHeaderLabels(["ID", "Unidades", "Ingreso (USD)", "Fecha", "Ingreso (CUP)"])
        else:
            self.sell_table.setColumnCount(4)
            self.sell_table.setHorizontalHeaderLabels(["ID", "Unidades", "Ingreso", "Fecha"])
        self.sell_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        if enabled:
            self.product_table.setColumnCount(6)
            self.product_table.setHorizontalHeaderLabels(
                ["Producto", "Stock", "Precio", "Costo", "Ganancia Esp. (USD)", "Ganancia Esp. (CUP)"]
            )
        else:
            self.product_table.setColumnCount(5)
            self.product_table.setHorizontalHeaderLabels(
                ["Producto", "Stock", "Precio", "Costo", "Ganancia Esp."]
            )
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.summary_table.setColumnCount(3 if enabled else 2)
        if enabled:
            self.summary_table.setHorizontalHeaderLabels(["Concepto", "Valor (USD)", "Valor (CUP)"])
        else:
            self.summary_table.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _load_reports(self):
        """Carga y muestra todos los reportes según el rango de fechas seleccionado"""
        self.entry_table.setSortingEnabled(False)
        self.out_table.setSortingEnabled(False)
        self.sell_table.setSortingEnabled(False)
        self.sales_by_product_table.setSortingEnabled(False)
        self.product_table.setSortingEnabled(False)

        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        self._current_start = start
        self._current_end = end

        use_conversion = self.convert_cb.isChecked()
        rate = Decimal(str(self.rate_input.value()))

        session = get_session()
        try:
            entries = get_entries(session, start, end)
            self._entries_data = entries
            self.entry_table.setRowCount(len(entries))
            for i, e in enumerate(entries):
                self.entry_table.setItem(i, 0, QTableWidgetItem(str(e.idEntry)))
                from src.models.product import Product
                product = session.get(Product, e.id_prod)
                name = product.name if product else str(e.id_prod)
                self.entry_table.setItem(i, 1, QTableWidgetItem(name))
                self.entry_table.setItem(i, 2, QTableWidgetItem(str(e.cant)))
                self.entry_table.setItem(i, 3, QTableWidgetItem(str(e.date)))

            outs = get_outs(session, start, end)
            self._outs_data = outs
            self.out_table.setRowCount(len(outs))
            for i, o in enumerate(outs):
                self.out_table.setItem(i, 0, QTableWidgetItem(str(o.idOut)))
                from src.models.product import Product
                product = session.get(Product, o.id_prod)
                name = product.name if product else str(o.id_prod)
                self.out_table.setItem(i, 1, QTableWidgetItem(name))
                self.out_table.setItem(i, 2, QTableWidgetItem(str(o.cant)))
                self.out_table.setItem(i, 3, QTableWidgetItem(o.destination))
                self.out_table.setItem(i, 4, QTableWidgetItem(str(o.date)))

            sells = get_sells(session, start, end)
            self._sells_data = sells
            self.sell_table.setRowCount(len(sells))
            for i, s in enumerate(sells):
                self.sell_table.setItem(i, 0, QTableWidgetItem(str(s.idSell)))
                self.sell_table.setItem(i, 1, QTableWidgetItem(str(s.cant)))
                if use_conversion:
                    converted = s.revenue * rate
                    self.sell_table.setItem(i, 2, QTableWidgetItem(f"${s.revenue}"))
                    self.sell_table.setItem(i, 3, QTableWidgetItem(str(s.date)))
                    self.sell_table.setItem(i, 4, QTableWidgetItem(f"${converted:.2f}"))
                else:
                    self.sell_table.setItem(i, 2, QTableWidgetItem(f"${s.revenue}"))
                    self.sell_table.setItem(i, 3, QTableWidgetItem(str(s.date)))

            sales_by_product = get_sales_by_product(session, start, end)
            self._sales_by_product_data = sales_by_product
            self.sales_by_product_table.setRowCount(len(sales_by_product))
            for i, row in enumerate(sales_by_product):
                self.sales_by_product_table.setItem(i, 0, QTableWidgetItem(row.name))
                self.sales_by_product_table.setItem(i, 1, QTableWidgetItem(str(row.total_sold)))

            stock_profit = get_stock_profit(session)
            self._product_data = stock_profit
            self.product_table.setRowCount(len(stock_profit))
            for i, row in enumerate(stock_profit):
                self.product_table.setItem(i, 0, QTableWidgetItem(row.name))
                self.product_table.setItem(i, 1, QTableWidgetItem(str(row.stock)))
                self.product_table.setItem(i, 2, QTableWidgetItem(f"${row.price}"))
                self.product_table.setItem(i, 3, QTableWidgetItem(f"${row.cost}"))
                if use_conversion:
                    converted_profit = row.expected_profit * rate
                    self.product_table.setItem(i, 4, QTableWidgetItem(f"${row.expected_profit:.2f}"))
                    self.product_table.setItem(i, 5, QTableWidgetItem(f"${converted_profit:.2f}"))
                else:
                    self.product_table.setItem(i, 4, QTableWidgetItem(f"${row.expected_profit:.2f}"))

            summary = get_summary(session, start, end)
            self._summary_data = summary
            revenue_val = summary["total_revenue"]
            cost_val = summary["total_cost"]
            profit_val = summary["total_profit"]
            self.summary_table.setItem(0, 0, QTableWidgetItem("Ingreso Total"))
            self.summary_table.setItem(0, 1, QTableWidgetItem(f"${revenue_val:.2f}"))
            self.summary_table.setItem(1, 0, QTableWidgetItem("Costo Total"))
            self.summary_table.setItem(1, 1, QTableWidgetItem(f"${cost_val:.2f}"))
            self.summary_table.setItem(2, 0, QTableWidgetItem("Ganancia Total"))
            self.summary_table.setItem(2, 1, QTableWidgetItem(f"${profit_val:.2f}"))
            if use_conversion:
                converted_revenue = revenue_val * rate
                converted_cost = cost_val * rate
                converted_profit = profit_val * rate
                self.summary_table.setItem(0, 2, QTableWidgetItem(f"${converted_revenue:.2f}"))
                self.summary_table.setItem(1, 2, QTableWidgetItem(f"${converted_cost:.2f}"))
                self.summary_table.setItem(2, 2, QTableWidgetItem(f"${converted_profit:.2f}"))
        except Exception as e:
            logger.exception("Error al cargar reportes:")
            QMessageBox.critical(self, "Error", f"Error al cargar reportes: {e}")
        finally:
            session.close()
            self.entry_table.setSortingEnabled(True)
            self.out_table.setSortingEnabled(True)
            self.sell_table.setSortingEnabled(True)
            self.sales_by_product_table.setSortingEnabled(True)
            self.product_table.setSortingEnabled(True)

    def _export_csv(self):
        """Exporta el reporte de la pestaña actual a un archivo CSV"""
        tab_index = self.tabs.currentIndex()
        tab_name = self.tabs.tabText(tab_index).lower()

        default_name = f"reporte_{tab_name}_{self._current_start}_{self._current_end}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar CSV", default_name, "CSV (*.csv)",
        )
        if not path:
            return

        if tab_index == 0:
            rows = self._entries_data
            headers = ["ID", "ID Producto", "Cantidad", "Fecha"]
        elif tab_index == 1:
            rows = self._outs_data
            headers = ["ID", "ID Producto", "Cantidad", "Destino", "Fecha"]
        elif tab_index == 2:
            rows = self._sells_data
            if self.convert_cb.isChecked():
                headers = ["ID", "Unidades", "Ingreso (USD)", "Fecha", "Ingreso (CUP)"]
            else:
                headers = ["ID", "Unidades", "Ingreso", "Fecha"]
        elif tab_index == 3:
            rows = self._sales_by_product_data
            headers = ["Producto", "Cantidad Vendida"]
        elif tab_index == 5:
            rows = self._product_data
            if self.convert_cb.isChecked():
                headers = ["Producto", "Stock", "Precio", "Costo", "Ganancia Esp. (USD)", "Ganancia Esp. (CUP)"]
            else:
                headers = ["Producto", "Stock", "Precio", "Costo", "Ganancia Esp."]
        else:
            data = self._summary_data
            if self.convert_cb.isChecked():
                headers = ["Concepto", "Valor (USD)", "Valor (CUP)"]
            else:
                headers = ["Concepto", "Valor"]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                if tab_index == 0:
                    writer.writerow([row.idEntry, row.id_prod, row.cant, row.date])
                elif tab_index == 1:
                    writer.writerow([row.idOut, row.id_prod, row.cant, row.destination, row.date])
                elif tab_index == 2:
                    if self.convert_cb.isChecked():
                        rate = Decimal(str(self.rate_input.value()))
                        converted = row.revenue * rate
                        writer.writerow([row.idSell, row.cant, str(row.revenue), row.date, f"{converted:.2f}"])
                    else:
                        writer.writerow([row.idSell, row.cant, str(row.revenue), row.date])
                elif tab_index == 3:
                    writer.writerow([row.name, row.total_sold])
                elif tab_index == 5:
                    if self.convert_cb.isChecked():
                        rate = Decimal(str(self.rate_input.value()))
                        converted = row.expected_profit * rate
                        writer.writerow([row.name, row.stock, str(row.price), str(row.cost), f"{row.expected_profit:.2f}", f"{converted:.2f}"])
                    else:
                        writer.writerow([row.name, row.stock, str(row.price), str(row.cost), f"{row.expected_profit:.2f}"])
                else:
                    if self.convert_cb.isChecked():
                        rate = Decimal(str(self.rate_input.value()))
                        rev = Decimal(str(data["total_revenue"]))
                        cost = Decimal(str(data["total_cost"]))
                        profit = Decimal(str(data["total_profit"]))
                        writer.writerow(["Ingreso Total", f"{rev:.2f}", f"{rev * rate:.2f}"])
                        writer.writerow(["Costo Total", f"{cost:.2f}", f"{cost * rate:.2f}"])
                        writer.writerow(["Ganancia Total", f"{profit:.2f}", f"{profit * rate:.2f}"])
                    else:
                        writer.writerow(["Ingreso Total", str(data["total_revenue"])])
                        writer.writerow(["Costo Total", str(data["total_cost"])])
                        writer.writerow(["Ganancia Total", str(data["total_profit"])])

        QMessageBox.information(self, "Exportado", f"Reporte guardado en:\n{path}")
