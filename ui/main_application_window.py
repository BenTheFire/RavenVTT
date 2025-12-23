from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from ui.main_menu_window import MainMenuWindow
from ui.uvtt_editor_window import UvttEditorWindow
from ui.character_editor_window import CharacterEditorWindow

class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DnD Toolbox")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add widgets
        self.main_menu = MainMenuWindow()
        self.uvtt_editor = UvttEditorWindow()
        self.character_editor = CharacterEditorWindow()

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.uvtt_editor)
        self.stacked_widget.addWidget(self.character_editor)

        # Create and add toolbars
        self.toolbars = [
            self.uvtt_editor.toolbar,
            self.uvtt_editor.grid_toolbar,
            self.uvtt_editor.drawing_toolbar,
            self.uvtt_editor.fow_toolbar,
            self.uvtt_editor.vbl_toolbar
        ]
        
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.uvtt_editor.toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.uvtt_editor.grid_toolbar)
        self.addToolBarBreak()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.uvtt_editor.drawing_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.uvtt_editor.fow_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.uvtt_editor.vbl_toolbar)

        # Connect signals
        self.main_menu.uvtt_editor_button.clicked.connect(self.show_uvtt_editor)
        self.main_menu.character_editor_button.clicked.connect(self.show_character_editor)
        self.uvtt_editor.show_main_menu_requested.connect(self.show_main_menu)
        self.character_editor.show_main_menu_requested.connect(self.show_main_menu)

        # Set initial view
        self.show_main_menu()

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu)
        self.menuBar().clear()
        for tb in self.toolbars:
            tb.setVisible(False)

    def show_uvtt_editor(self):
        self.stacked_widget.setCurrentWidget(self.uvtt_editor)
        self.menuBar().clear()
        self.menuBar().addMenu(self.uvtt_editor.file_menu)
        self.menuBar().addMenu(self.uvtt_editor.edit_menu)
        
        self.uvtt_editor.toolbar.setVisible(True)
        self.uvtt_editor.grid_toolbar.setVisible(True)
        self.uvtt_editor.on_main_tool_selected()

    def show_character_editor(self):
        self.stacked_widget.setCurrentWidget(self.character_editor)
        self.menuBar().clear()
        self.menuBar().addMenu(self.character_editor.file_menu)
        self.menuBar().addMenu(self.character_editor.edit_menu)
        for tb in self.toolbars:
            tb.setVisible(False)
