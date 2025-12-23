from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from utils.dice_roller import roll

class DiceRollerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dice Roller")
        
        self.layout = QVBoxLayout(self)
        
        # Input and Roll Button
        input_layout = QHBoxLayout()
        self.dice_string_input = QLineEdit()
        self.dice_string_input.setPlaceholderText("e.g., 2d6 + 1d20A + 5")
        roll_button = QPushButton("Roll")
        roll_button.clicked.connect(self._perform_roll)
        input_layout.addWidget(self.dice_string_input)
        input_layout.addWidget(roll_button)
        self.layout.addLayout(input_layout)
        
        # Results Display
        self.results_layout = QVBoxLayout()
        self.layout.addLayout(self.results_layout)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)
        
        # Total Display
        self.total_label = QLabel("Total: 0")
        self.total_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.total_label)

    def _perform_roll(self):
        # Clear previous results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        dice_string = self.dice_string_input.text()
        if not dice_string:
            return
            
        results, grand_total = roll(dice_string)
        
        for result in results:
            self.results_layout.addWidget(QLabel(result['text']))
            
        self.total_label.setText(f"Total: {grand_total}")
