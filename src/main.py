
from PyQt6.QtWidgets import QApplication, QWidget
import sys

def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Mi App")
    window.resize(300, 200)
    window.show()

    print("Aplicación iniciada correctamente.")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
