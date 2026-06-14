from PyQt6.QtWidgets import QApplication, QWidget
import sys

from src.database.session import engine
from src.database.base import Base


def main():
    Base.metadata.create_all(bind=engine)

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Sistema de Gestión de Inventario")
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
