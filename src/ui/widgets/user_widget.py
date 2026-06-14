from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QFormLayout, QComboBox, QDialog, QMessageBox, QHeaderView,
)
from src.database.session import get_session
from src.services.auth_service import require_admin
from src.services.user_service import (
    create_user, get_all_users, delete_user,
)
from src.models.user import User


class UserWidget(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.current_user = user
        require_admin(self.current_user)
        self._setup_ui()
        self._load_users()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Gestión de Usuarios (Admin)")
        header.setObjectName("header")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Nuevo Usuario")
        self.add_btn.setObjectName("success")
        self.add_btn.clicked.connect(self._add_user)
        btn_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self._load_users)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Usuario", "Rol", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _load_users(self):
        session = get_session()
        try:
            users = get_all_users(session)
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(users))
            for i, u in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(str(u.id)))
                self.table.setItem(i, 1, QTableWidgetItem(u.username))
                self.table.setItem(i, 2, QTableWidgetItem(u.role))
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("danger")
                delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                delete_btn.clicked.connect(lambda checked, uid=u.id: self._delete_user(uid))
                self.table.setCellWidget(i, 3, delete_btn)
            self.table.setSortingEnabled(True)
        finally:
            session.close()

    def _add_user(self):
        try:
            require_admin(self.current_user)
        except PermissionError as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = get_session()
            try:
                data = dialog.get_data()
                create_user(session, data["username"], data["password"], data["role"])
                self._load_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()

    def _delete_user(self, user_id: int):
        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar este usuario?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                delete_user(session, user_id, self.current_user)
                self._load_users()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Usuario")
        self.setFixedSize(320, 220)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario")
        form.addRow("Usuario:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Contraseña:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["vendedor", "admin"])
        form.addRow("Rol:", self.role_combo)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("success")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("danger")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        username = self.username_input.text().strip()
        if not username:
            raise ValueError("Usuario: el nombre de usuario no puede estar vacío")
        password = self.password_input.text().strip()
        if not password:
            raise ValueError("Contraseña: no puede estar vacía")
        return {
            "username": username,
            "password": password,
            "role": self.role_combo.currentText(),
        }
