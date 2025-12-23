from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class MainMenuWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.uvtt_editor_button = QPushButton("uVTT Editor")
        layout.addWidget(self.uvtt_editor_button)

        self.vtt_renderer_button = QPushButton("VTT Renderer (Not Implemented)")
        self.vtt_renderer_button.setEnabled(False)
        layout.addWidget(self.vtt_renderer_button)

        self.character_editor_button = QPushButton("Character Editor")
        layout.addWidget(self.character_editor_button)

        self.dm_editor_button = QPushButton("DM Editor (Not Implemented)")
        self.dm_editor_button.setEnabled(False)
        layout.addWidget(self.dm_editor_button)
