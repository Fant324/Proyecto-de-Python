from PyQt6.QtWidgets import QApplication, QWidget
import sys

# Importa tu ventana principal (cuando la crees)
# from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Mi App")
    window.resize(300, 200)
    window.show()

    print("Aplicación iniciada correctamente.")

    sys.exit(app.exec())
