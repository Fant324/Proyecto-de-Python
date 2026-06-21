"""Módulo de la ventana principal de la aplicación"""

import logging
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMessageBox,
    QApplication,
)
from src.models.user import User
from src.ui.title_bar import TitleBar

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Ventana principal con menú lateral y panel de contenido apilado"""
    def __init__(self, user: User):
        """Inicializa la ventana principal con el usuario autenticado"""
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.current_user = user
        self.setWindowTitle(f"Inventario - {user.username} ({user.role})")
        self.resize(950, 680)
        self._setup_ui()
        QShortcut(QKeySequence("F11"), self).activated.connect(self._toggle_fullscreen)

    def _toggle_fullscreen(self):
        """Alterna entre pantalla completa y modo ventana"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _close_app(self):
        """Cierra la aplicación completamente"""
        QApplication.quit()

    def _setup_ui(self):
        """Configura la interfaz: barra de título, menú lateral y panel apilado"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title = f"Inventario - {self.current_user.username} ({self.current_user.role})"
        self.title_bar = TitleBar(self, title, close_callback=self._close_app)
        main_layout.addWidget(self.title_bar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        menu_panel = QWidget()
        menu_panel.setObjectName("menuPanel")
        menu_panel.setStyleSheet(
            "QWidget#menuPanel { background-color: #1a2530; min-width: 180px; max-width: 180px; }"
        )
        self.menu_layout = QVBoxLayout(menu_panel)
        self.menu_layout.setContentsMargins(8, 12, 8, 12)
        self.menu_layout.setSpacing(4)

        menu_title = QLabel("Menú")
        menu_title.setStyleSheet("color: #8a9ba8; font-weight: bold; font-size: 12px; padding: 4px 8px;")
        self.menu_layout.addWidget(menu_title)

        self._build_menu()

        content.addWidget(menu_panel)

        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(500)
        content.addWidget(self.stack, 1)

        main_layout.addLayout(content)
        self._show_default_widget()

    def _build_menu(self):
        """Construye los botones del menú lateral según el rol del usuario"""
        role = self.current_user.role
        if role in ("admin", "almacen", "vendedor"):
            self.add_menu_btn("Productos", self._show_products)
        if role in ("admin", "almacen"):
            self.add_menu_btn("Entradas", self._show_entries)
            self.add_menu_btn("Salidas", self._show_outs)
        if role in ("admin", "vendedor"):
            self.add_menu_btn("Ventas", self._show_sells)
        if role == "admin":
            self.add_menu_btn("Reportes", self._show_reports)
            self.add_menu_btn("Usuarios", self._show_users)

        self.menu_layout.addSpacing(20)

        logout_btn = QPushButton("Cerrar Sesión")
        logout_btn.setObjectName("logout")
        logout_btn.setMinimumHeight(40)
        logout_btn.clicked.connect(self._logout)
        self.menu_layout.addWidget(logout_btn)

        self.menu_layout.addStretch()

    def add_menu_btn(self, text, callback):
        """Crea y agrega un botón con estilo al menú lateral"""
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

    def _show_default_widget(self):
        """Muestra el widget por defecto según el rol"""
        if self.current_user.role == "vendedor":
            self._show_sells()
        else:
            self._show_products()

    def _show_products(self):
        """Muestra el widget de gestión de productos"""
        from src.ui.widgets.product_widget import ProductWidget
        self._show_widget(ProductWidget)

    def _show_entries(self):
        """Muestra el widget de registro de entradas"""
        from src.ui.widgets.entry_widget import EntryWidget
        self._show_widget(EntryWidget)

    def _show_outs(self):
        """Muestra el widget de registro de salidas"""
        from src.ui.widgets.out_widget import OutWidget
        self._show_widget(OutWidget)

    def _show_sells(self):
        """Muestra el widget de registro de ventas"""
        from src.ui.widgets.sell_widget import SellWidget
        self._show_widget(SellWidget)

    def _show_reports(self):
        """Muestra el widget de reportes (solo admin)"""
        from src.ui.widgets.report_widget import ReportWidget
        self._show_widget(ReportWidget)

    def _show_users(self):
        """Muestra el widget de gestión de usuarios (solo admin)"""
        from src.ui.widgets.user_widget import UserWidget
        try:
            self._show_widget(UserWidget)
        except PermissionError as e:
            logger.exception("Error al mostrar usuarios:")
            QMessageBox.warning(self, "Error", str(e))

    def _show_widget(self, widget_class):
        """Muestra o agrega un widget en el panel apilado; reusa instancias existentes"""
        for i in range(self.stack.count()):
            if isinstance(self.stack.widget(i), widget_class):
                self.stack.setCurrentIndex(i)
                return
        widget = widget_class(self.current_user)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def _logout(self):
        """Cierra sesión y abre la ventana de inicio de sesión"""
        from src.ui.login_window import LoginWindow
        self.close()
        self.deleteLater()
        self._login_window = LoginWindow(self._on_relogin)
        self._login_window.show()

    def _on_relogin(self, user):
        """Crea una nueva ventana principal tras un inicio de sesión exitoso"""
        self._new_main = MainWindow(user)
        self._new_main.show()
        self._new_main.showFullScreen()
