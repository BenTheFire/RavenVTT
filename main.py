import sys
from PyQt6.QtWidgets import QApplication
from ui.main_application_window import MainApplicationWindow

def main():
    app = QApplication(sys.argv)
    window = MainApplicationWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
