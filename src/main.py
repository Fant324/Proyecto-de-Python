import sys
from PyQt6.QtWidgets import QApplication
from src.database.session import engine
from src.database.base import Base
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow


def main():
    Base.metadata.create_all(bind=engine)

    app = QApplication(sys.argv)

    def on_login_success(user):
        main_win = MainWindow(user)
        main_win.show()
        main_win.destroyed.connect(app.quit)

    login = LoginWindow(on_login_success)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
