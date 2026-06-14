from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox,
)
from src.database.session import get_session
from src.services.auth_service import authenticate_user


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Inicio de Sesión - Inventario")
        self.setFixedSize(350, 220)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("Sistema de Gestión de Inventario")
        self.title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        self.title.setAlignment(self.title.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.clicked.connect(self._handle_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def _handle_login(self):
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
