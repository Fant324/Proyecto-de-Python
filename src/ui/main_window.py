from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
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
        self.resize(950, 680)
        self._setup_ui()
        QShortcut(QKeySequence("F11"), self).activated.connect(self._toggle_fullscreen)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_bar = QWidget()
        header_bar.setObjectName("headerBar")
        header_bar.setStyleSheet(
            "QWidget#headerBar { background-color: #2d2d2d; padding: 12px 20px; }"
        )
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(20, 8, 20, 8)

        header = QLabel(f"Bienvenido, {self.current_user.username} ({self.current_user.role})")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        fullscreen_btn = QPushButton("⛶")
        fullscreen_btn.setToolTip("Pantalla completa (F11)")
        fullscreen_btn.setFixedSize(32, 32)
        fullscreen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fullscreen_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #aaaaaa; "
            "font-size: 18px; border-radius: 4px; padding: 0px; }"
            "QPushButton:hover { background-color: #3a3a3a; color: #ffffff; }"
        )
        fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        header_layout.addWidget(fullscreen_btn)

        main_layout.addWidget(header_bar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        menu_panel = QWidget()
        menu_panel.setObjectName("menuPanel")
        menu_panel.setStyleSheet(
            "QWidget#menuPanel { background-color: #252525; min-width: 180px; max-width: 180px; }"
        )
        self.menu_layout = QVBoxLayout(menu_panel)
        self.menu_layout.setContentsMargins(8, 12, 8, 12)
        self.menu_layout.setSpacing(4)

        menu_title = QLabel("Menú")
        menu_title.setStyleSheet("color: #888888; font-weight: bold; font-size: 12px; padding: 4px 8px;")
        self.menu_layout.addWidget(menu_title)

        self._build_menu()

        content.addWidget(menu_panel)

        stack_container = QWidget()
        stack_layout = QHBoxLayout(stack_container)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.addStretch()

        self.stack = QStackedWidget()
        self.stack.setMaximumWidth(1100)
        stack_layout.addWidget(self.stack)

        stack_layout.addStretch()
        content.addWidget(stack_container, 1)

        main_layout.addLayout(content)

    def _build_menu(self):
        self.add_menu_btn("Productos", self._show_products)
        self.add_menu_btn("Entradas", self._show_entries)
        self.add_menu_btn("Salidas", self._show_outs)
        self.add_menu_btn("Ventas", self._show_sells)
        self.add_menu_btn("Reportes", self._show_reports)

        if self.current_user.role == "admin":
            self.add_menu_btn("Usuarios", self._show_users)

        self.menu_layout.addSpacing(20)

        logout_btn = QPushButton("Cerrar Sesión")
        logout_btn.setObjectName("logout")
        logout_btn.setMinimumHeight(40)
        logout_btn.clicked.connect(self._logout)
        self.menu_layout.addWidget(logout_btn)

        self.menu_layout.addStretch()

    def add_menu_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setObjectName("menuBtn")
        btn.setMinimumHeight(42)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton#menuBtn { background-color: transparent; color: #cccccc; "
            "text-align: left; padding: 8px 12px; border-radius: 8px; font-weight: normal; }"
            "QPushButton#menuBtn:hover { background-color: #3a3a3a; }"
            "QPushButton#menuBtn:pressed { background-color: #505050; }"
        )
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
        try:
            self._show_widget(UserWidget)
        except PermissionError as e:
            QMessageBox.warning(self, "Error", str(e))

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
        self.deleteLater()
        self._login_window = LoginWindow(self._on_relogin)
        self._login_window.show()

    def _on_relogin(self, user):
        self._new_main = MainWindow(user)
        self._new_main.show()
