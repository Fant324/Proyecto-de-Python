import sys
from PyQt6.QtWidgets import QApplication
from src.database.session import engine
from src.database.base import Base
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow


def main():
    Base.metadata.create_all(bind=engine)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    login = LoginWindow(lambda user: MainWindow(user).show())
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
