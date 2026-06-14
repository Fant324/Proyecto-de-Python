import sys
import os
import logging
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QScreen
from src.database.session import engine
from src.database.base import Base
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def center_window(window):
    screen = QApplication.primaryScreen().geometry()
    window.move(
        (screen.width() - window.width()) // 2,
        (screen.height() - window.height()) // 2,
    )


def main():
    logger.info("Iniciando Sistema de Gestión de Inventario")
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos lista")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    try:
        with open(qss_path) as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        logger.warning("styles.qss no encontrado")

    main_window_ref = []

    def on_login_success(user):
        w = MainWindow(user)
        w.show()
        w.raise_()
        w.activateWindow()
        main_window_ref.append(w)
        QTimer.singleShot(150, w.showFullScreen)

    login = LoginWindow(on_login_success)
    login.show()
    center_window(login)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
