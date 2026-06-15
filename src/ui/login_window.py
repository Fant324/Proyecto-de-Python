"""Módulo de la ventana de inicio de sesión"""

import logging
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox,
)
from src.database.session import get_session
from src.services.auth_service import authenticate_user
from src.ui.title_bar import TitleBar

logger = logging.getLogger(__name__)


class LoginWindow(QWidget):
    """Ventana de inicio de sesión con formulario de usuario y contraseña"""
    def __init__(self, on_login_success):
        """Inicializa la ventana con el callback para inicio de sesión exitoso"""
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.on_login_success = on_login_success
        self.setWindowTitle("Inicio de Sesión - Inventario")
        self.setMinimumSize(360, 280)
        self._setup_ui()

    def showEvent(self, event):
        """Centra la ventana en la pantalla al mostrarse"""
        super().showEvent(event)
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _setup_ui(self):
        """Construye la interfaz del formulario de inicio de sesión"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = TitleBar(self, "Inicio de Sesión")
        layout.addWidget(self.title_bar)

        form = QVBoxLayout()
        form.setContentsMargins(30, 20, 30, 24)
        form.setSpacing(14)

        self.title = QLabel("Sistema de\nGestión de Inventario")
        self.title.setObjectName("header")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)
        form.addWidget(self.title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        form.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addWidget(self.password_input)

        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.setObjectName("success")
        self.login_btn.clicked.connect(self._handle_login)
        form.addWidget(self.login_btn)

        layout.addLayout(form)
        self.setLayout(layout)

    def _handle_login(self):
        """Valida credenciales e invoca el callback de inicio de sesión exitoso"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Usuario y contraseña requeridos")
            return

        session = get_session()
        try:
            user = authenticate_user(session, username, password)
            if user:
                self.on_login_success(user)
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos")
        finally:
            session.close()
