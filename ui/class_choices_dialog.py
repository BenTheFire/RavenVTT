from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout, QDialogButtonBox, 
                             QCheckBox, QLabel, QRadioButton, QHBoxLayout, QButtonGroup)

class ClassChoicesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Class Choices")
        
        self.layout = QVBoxLayout(self)
        
        # This will be the main container for dynamically added choices
        self.choices_layout = QVBoxLayout()
        self.layout.addLayout(self.choices_layout)
        
        # OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.results = {}

    def populate_choices(self, class_data):
        # Clear previous choices
        while self.choices_layout.count():
            child = self.choices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.results = {}

        # Skill Proficiencies
        skill_info = class_data.get("skill_proficiency", {})
        if skill_info:
            self._populate_skill_choices(skill_info)

        # Equipment Choices
        equipment_info = class_data.get("equipment_choices", [])
        if equipment_info:
            self._populate_equipment_choices(equipment_info)

    def _populate_skill_choices(self, skill_info):
        group = QGroupBox("Skill Proficiencies")
        layout = QVBoxLayout(group)
        
        choose = skill_info.get("choose", 0)
        options = skill_info.get("from", [])
        
        layout.addWidget(QLabel(f"Choose {choose} from the following:"))
        
        self.skill_checkboxes = []
        for skill in options:
            cb = QCheckBox(skill.replace("_", " ").title())
            self.skill_checkboxes.append(cb)
            layout.addWidget(cb)
            
        self.choices_layout.addWidget(group)

    def _populate_equipment_choices(self, equipment_info):
        group = QGroupBox("Starting Equipment")
        layout = QFormLayout(group)
        
        self.equipment_groups = []
        for i, choice in enumerate(equipment_info):
            choice_layout = QHBoxLayout()
            button_group = QButtonGroup(self)
            self.equipment_groups.append(button_group)
            
            # Assuming choices are 'a', 'b', 'c', etc.
            for key, value in choice.items():
                # This is a simplified representation. A full implementation would parse the item list.
                rb = QRadioButton(str(value)) 
                button_group.addButton(rb)
                choice_layout.addWidget(rb)
                if key == 'a': # Select the first option by default
                    rb.setChecked(True)

            layout.addRow(f"Choice {i+1}:", choice_layout)
            
        self.choices_layout.addWidget(group)

    def accept(self):
        # Logic to gather selected choices before closing
        self.results['skills'] = [cb.text() for cb in self.skill_checkboxes if cb.isChecked()]
        # In a full implementation, we would gather equipment choices here too.
        super().accept()
