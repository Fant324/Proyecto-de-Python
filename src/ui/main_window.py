from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMessageBox,
)
from src.models.user import User


class MainWindow(QMainWindow):
    def __init__(self, user: User):
        super().__init__()
        self.current_user = user
        self.setWindowTitle(f"Inventario - {user.username} ({user.role})")
        self.resize(900, 650)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header = QLabel(f"Bienvenido, {self.current_user.username} ({self.current_user.role})")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header)

        content = QHBoxLayout()

        self.menu_layout = QVBoxLayout()
        self.menu_layout.setSpacing(5)
        self.menu_layout.addWidget(QLabel("Menú"))

        self._build_menu()

        content.addLayout(self.menu_layout)

        self.stack = QStackedWidget()
        content.addWidget(self.stack, 1)

        main_layout.addLayout(content)

    def _build_menu(self):
        self.add_menu_btn("Productos", self._show_products)
        self.add_menu_btn("Entradas", self._show_entries)
        self.add_menu_btn("Salidas", self._show_outs)
        self.add_menu_btn("Ventas", self._show_sells)
        self.add_menu_btn("Reportes", self._show_reports)

        if self.current_user.role == "admin":
            self.add_menu_btn("Usuarios", self._show_users)

        logout_btn = QPushButton("Cerrar Sesión")
        logout_btn.clicked.connect(self._logout)
        self.menu_layout.addWidget(logout_btn)

        self.menu_layout.addStretch()

    def add_menu_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setMinimumHeight(40)
        btn.clicked.connect(callback)
        self.menu_layout.addWidget(btn)

    def _show_products(self):
        from src.ui.widgets.product_widget import ProductWidget
        self._show_widget(ProductWidget)

    def _show_entries(self):
        from src.ui.widgets.entry_widget import EntryWidget
        self._show_widget(EntryWidget)

    def _show_outs(self):
        from src.ui.widgets.out_widget import OutWidget
        self._show_widget(OutWidget)

    def _show_sells(self):
        from src.ui.widgets.sell_widget import SellWidget
        self._show_widget(SellWidget)

    def _show_reports(self):
        from src.ui.widgets.report_widget import ReportWidget
        self._show_widget(ReportWidget)

    def _show_users(self):
        from src.ui.widgets.user_widget import UserWidget
        self._show_widget(UserWidget)

    def _show_widget(self, widget_class):
        for i in range(self.stack.count()):
            if isinstance(self.stack.widget(i), widget_class):
                self.stack.setCurrentIndex(i)
                return
        widget = widget_class(self.current_user)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def _logout(self):
        from src.ui.login_window import LoginWindow
        self.close()
        login = LoginWindow(lambda user: (
            MainWindow(user).show()
        ))
        login.show()
