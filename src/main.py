import sys
import logging
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
    logger.info("Iniciando Sistema de Gestión de Inventario")
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos lista")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    login = LoginWindow(lambda user: MainWindow(user).show())
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
