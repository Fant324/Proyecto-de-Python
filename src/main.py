"""Punto de entrada principal - inicializa la aplicación PyQt6, base de datos y ventanas de login/principal"""

import sys
import logging
from pathlib import Path
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from src.database.session import engine
from src.database.base import Base
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Inicia la aplicación: crea tablas, configura la ventana de login y ejecuta el bucle de eventos de Qt"""
    logger.info("Iniciando Sistema de Gestión de Inventario")
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos lista")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    qss_path = Path(__file__).parent / "ui" / "styles_dark.qss"
    try:
        with open(qss_path, encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        logger.warning("styles_dark.qss no encontrado, se usará estilo por defecto")

    main_window_ref = []

    def on_login_success(user):
        """Callback ejecutado tras autenticación exitosa; crea la ventana principal y la muestra en pantalla completa"""
        w = MainWindow(user)
        w.show()
        w.raise_()
        w.activateWindow()
        main_window_ref.append(w)
        QTimer.singleShot(150, w.showFullScreen)

    login = LoginWindow(on_login_success)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
