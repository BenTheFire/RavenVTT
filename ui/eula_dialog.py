from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QTextEdit, QWidget
from PyQt6.QtCore import Qt

class EulaDialog(QDialog):
    def __init__(self, eula_path: str, license_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("End-User License Agreement & License")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # EULA Tab
        eula_widget = QWidget()
        eula_layout = QVBoxLayout(eula_widget)
        self.eula_text_edit = QTextEdit()
        self.eula_text_edit.setReadOnly(True)
        try:
            with open(eula_path, 'r', encoding='utf-8') as f:
                self.eula_text_edit.setPlainText(f.read())
        except FileNotFoundError:
            self.eula_text_edit.setPlainText("EULA file not found.")
        eula_layout.addWidget(self.eula_text_edit)
        self.tabs.addTab(eula_widget, "EULA")

        # License Tab
        license_widget = QWidget()
        license_layout = QVBoxLayout(license_widget)
        self.license_text_edit = QTextEdit()
        self.license_text_edit.setReadOnly(True)
        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                self.license_text_edit.setPlainText(f.read())
        except FileNotFoundError:
            self.license_text_edit.setPlainText("LICENSE file not found.")
        license_layout.addWidget(self.license_text_edit)
        self.tabs.addTab(license_widget, "LICENSE")

        # Buttons
        button_layout = QHBoxLayout()
        self.accept_button = QPushButton("Accept")
        self.accept_button.clicked.connect(self.accept)
        self.reject_button = QPushButton("Reject")
        self.reject_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.reject_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)
