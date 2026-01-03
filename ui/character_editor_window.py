import os
import json
import math
import base64
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel, QMenu, 
                             QScrollArea, QGridLayout, QGroupBox, QLineEdit, QSpinBox, QCheckBox, QFormLayout,
                             QComboBox, QSpacerItem, QSizePolicy, QFileDialog, QTextEdit, QMessageBox)
from ui.class_choices_dialog import ClassChoicesDialog
from ui.dice_roller_dialog import DiceRollerDialog
from ui.inventory_tab import InventoryTab

class CharacterEditorWindow(QWidget):
    show_main_menu_requested = pyqtSignal()

    # region Initialization and Core Setup
    def __init__(self):
        super().__init__()
        
        self.is_dirty = False
        self.current_character_path = None
        self.class_data = {}
        self.character_data = {}
        self._load_class_data()

        self.save_proficiencies = {}
        self.skill_proficiencies = {}
        self.ability_scores = {}
        self.ability_modifiers = {}
        self.skill_values = {}
        self.save_values = {}
        self.death_save_successes = []
        self.death_save_failures = []

        main_layout = QVBoxLayout(self)
        
        top_bar_layout = QHBoxLayout()
        self.main_menu_button = QPushButton("<< Main Menu")
        top_bar_layout.addWidget(self.main_menu_button)
        top_bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(top_bar_layout)
        
        self._create_menus()
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self._setup_char_info_tab()
        self._setup_roleplay_info_tab()
        self._setup_inventory_tab()
        self._setup_placeholder_tabs()

        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.dice_roller_button = QPushButton("Dice Roller")
        self.dice_roller_button.clicked.connect(self._open_dice_roller)
        bottom_bar_layout.addWidget(self.dice_roller_button)
        main_layout.addLayout(bottom_bar_layout)

        self._connect_signals()
        self._update_all_calculations()
        self.is_dirty = False
    # endregion

    # region Menus and Dialogs
    def _create_menus(self):
        self.file_menu = QMenu("&File", self)
        new_char_action = QAction("&New Character", self)
        new_char_action.triggered.connect(self._new_character)
        load_char_action = QAction("&Load Character", self)
        load_char_action.triggered.connect(self._load_character)
        save_action = QAction("&Save", self)
        save_action.triggered.connect(self._save_character)
        save_char_as_action = QAction("Save &As...", self)
        save_char_as_action.triggered.connect(self._save_character_as)
        self.file_menu.addActions([new_char_action, load_char_action, save_action, save_char_as_action])
        
        self.edit_menu = QMenu("&Edit", self)
        self.edit_menu.addActions([QAction("&Undo", self), QAction("&Redo", self)])

    def _open_dice_roller(self):
        dialog = DiceRollerDialog(self)
        dialog.exec()
    
    def _check_for_unsaved_changes(self):
        if not self.is_dirty:
            return True
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("You have unsaved changes.")
        msg_box.setInformativeText("Do you want to save your changes?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Save)
        
        ret = msg_box.exec()
        
        if ret == QMessageBox.StandardButton.Save:
            return self._save_character()
        elif ret == QMessageBox.StandardButton.Discard:
            return True
        return False
    # endregion

    # region UI Setup
    def _setup_char_info_tab(self):
        self.char_info_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        header_group = QGroupBox("Character Overview")
        header_layout = QHBoxLayout(header_group)
        self.sprite_label = QLabel("Click to Upload\nCharacter Sprite")
        self.sprite_label.mousePressEvent = self._upload_sprite
        self.sprite_label.setFixedSize(150, 150)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_label.setStyleSheet("border: 1px solid grey; cursor: pointer;")
        header_layout.addWidget(self.sprite_label)
        
        details_layout = QVBoxLayout()
        
        name_level_layout = QHBoxLayout()
        self.name_edit = QLineEdit(placeholderText="Character Name")
        name_level_layout.addWidget(self.name_edit)
        self.level_spinbox = QSpinBox(prefix="Level: ", minimum=1)
        self.level_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        name_level_layout.addWidget(self.level_spinbox)
        details_layout.addLayout(name_level_layout)
        
        class_bg_player_layout = QGridLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(sorted(self.class_data.keys()))
        self.background_edit = QLineEdit(placeholderText="Background")
        self.player_name_edit = QLineEdit(placeholderText="Player Name")
        class_bg_player_layout.addWidget(self.class_combo, 0, 0)
        class_bg_player_layout.addWidget(self.background_edit, 0, 1)
        class_bg_player_layout.addWidget(self.player_name_edit, 0, 2)
        details_layout.addLayout(class_bg_player_layout)

        race_align_xp_layout = QGridLayout()
        self.race_edit = QLineEdit(placeholderText="Race")
        self.alignment_edit = QLineEdit(placeholderText="Alignment")
        self.exp_spinbox = QSpinBox(prefix="XP: ")
        self.exp_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.exp_spinbox.setMaximum(1000000)
        race_align_xp_layout.addWidget(self.race_edit, 0, 0)
        race_align_xp_layout.addWidget(self.alignment_edit, 0, 1)
        race_align_xp_layout.addWidget(self.exp_spinbox, 0, 2)
        details_layout.addLayout(race_align_xp_layout)

        header_layout.addLayout(details_layout)
        main_layout.addWidget(header_group)

        body_layout = QGridLayout()

        left_col_layout = QVBoxLayout()
        scores_group = QGroupBox("Ability Scores")
        scores_layout = QGridLayout(scores_group)
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        for i, ability in enumerate(abilities):
            ability_key = ability.lower()
            scores_layout.addWidget(QLabel(ability), i, 0)
            score_spinbox = QSpinBox(minimum=1, maximum=30)
            score_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            modifier_label = QLineEdit(readOnly=True)
            modifier_label.setFixedWidth(40)
            self.ability_scores[ability_key] = score_spinbox
            self.ability_modifiers[ability_key] = modifier_label
            scores_layout.addWidget(score_spinbox, i, 1)
            scores_layout.addWidget(modifier_label, i, 2)
        left_col_layout.addWidget(scores_group)

        prof_group = QGroupBox("Proficiencies")
        prof_layout = QVBoxLayout(prof_group)
        self.proficiencies_list = QTextEdit(readOnly=True)
        prof_layout.addWidget(self.proficiencies_list)
        left_col_layout.addWidget(prof_group)
        left_col_layout.addStretch()
        body_layout.addLayout(left_col_layout, 0, 0)

        center_col_layout = QVBoxLayout()
        saves_group = QGroupBox("Saving Throws")
        saves_layout = QGridLayout(saves_group)
        for i, ability in enumerate(abilities):
            checkbox = QCheckBox()
            value_label = QLineEdit(readOnly=True)
            self.save_proficiencies[ability.lower()] = checkbox
            self.save_values[ability.lower()] = value_label
            saves_layout.addWidget(checkbox, i, 0)
            saves_layout.addWidget(QLabel(ability), i, 1)
            saves_layout.addWidget(value_label, i, 2)
        center_col_layout.addWidget(saves_group)

        skills_group = QGroupBox("Skills")
        skills_layout = QGridLayout(skills_group)
        skills_map = {"Acrobatics": "dex", "Animal Handling": "wis", "Arcana": "int", "Athletics": "str", "Deception": "cha", "History": "int", "Insight": "wis", "Intimidation": "cha", "Investigation": "int", "Medicine": "wis", "Nature": "int", "Perception": "wis", "Performance": "cha", "Persuasion": "cha", "Religion": "int", "Sleight of Hand": "dex", "Stealth": "dex", "Survival": "wis"}
        for i, (skill, ability_short) in enumerate(skills_map.items()):
            checkbox = QCheckBox()
            value_label = QLineEdit(readOnly=True)
            skill_key = skill.lower().replace(" ", "_")
            self.skill_proficiencies[skill_key] = checkbox
            self.skill_values[skill_key] = value_label
            skills_layout.addWidget(checkbox, i, 0)
            skills_layout.addWidget(QLabel(f"{skill} ({ability_short.upper()})"), i, 1)
            skills_layout.addWidget(value_label, i, 2)
        center_col_layout.addWidget(skills_group)
        body_layout.addLayout(center_col_layout, 0, 1, 2, 1)

        right_col_layout = QVBoxLayout()
        combat_group = QGroupBox("Combat")
        combat_layout = QFormLayout(combat_group)
        self.prof_bonus_label = QLineEdit(readOnly=True)
        self.ac_edit = QLineEdit()
        self.initiative_edit = QLineEdit(readOnly=True)
        self.speed_edit = QLineEdit()
        self.inspiration_spinbox = QSpinBox(maximum=10)
        self.inspiration_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        combat_layout.addRow("Proficiency Bonus:", self.prof_bonus_label)
        combat_layout.addRow("Inspiration:", self.inspiration_spinbox)
        combat_layout.addRow("Armor Class:", self.ac_edit)
        combat_layout.addRow("Initiative:", self.initiative_edit)
        combat_layout.addRow("Speed:", self.speed_edit)
        right_col_layout.addWidget(combat_group)

        hp_group = QGroupBox("Hit Points")
        hp_layout = QGridLayout(hp_group)
        self.max_hp_spinbox = QSpinBox(maximum=999)
        self.max_hp_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.current_hp_spinbox = QSpinBox(maximum=999)
        self.current_hp_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.temp_hp_spinbox = QSpinBox(maximum=999)
        self.temp_hp_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        hp_layout.addWidget(QLabel("Max:"), 0, 0)
        hp_layout.addWidget(self.max_hp_spinbox, 0, 1)
        hp_layout.addWidget(QLabel("Current:"), 1, 0)
        hp_layout.addWidget(self.current_hp_spinbox, 1, 1)
        hp_layout.addWidget(QLabel("Temp:"), 2, 0)
        hp_layout.addWidget(self.temp_hp_spinbox, 2, 1)
        
        death_saves_group = QGroupBox("Death Saves")
        death_saves_layout = QHBoxLayout(death_saves_group)
        death_saves_layout.addWidget(QLabel("Successes:"))
        for i in range(3):
            cb = QCheckBox()
            self.death_save_successes.append(cb)
            death_saves_layout.addWidget(cb)
        death_saves_layout.addStretch()
        death_saves_layout.addWidget(QLabel("Failures:"))
        for i in range(3):
            cb = QCheckBox()
            self.death_save_failures.append(cb)
            death_saves_layout.addWidget(cb)
        hp_layout.addLayout(death_saves_layout, 3, 0, 1, 2)
        
        hit_dice_group = QGroupBox("Hit Dice")
        hit_dice_layout = QFormLayout(hit_dice_group)
        self.hit_dice_total_label = QLineEdit(readOnly=True)
        self.hit_dice_current_spinbox = QSpinBox()
        self.hit_dice_current_spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        hit_dice_layout.addRow("Total:", self.hit_dice_total_label)
        hit_dice_layout.addRow("Current:", self.hit_dice_current_spinbox)
        hp_layout.addWidget(hit_dice_group, 4, 0, 1, 2)
        right_col_layout.addWidget(hp_group)

        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        self.actions_tabs = QTabWidget()
        self.actions_tabs.addTab(QTextEdit(readOnly=True), "Actions")
        self.actions_tabs.addTab(QTextEdit(readOnly=True), "Bonus Actions")
        self.actions_tabs.addTab(QTextEdit(readOnly=True), "Reactions")
        self.actions_tabs.addTab(QTextEdit(readOnly=True), "Free Actions")
        actions_layout.addWidget(self.actions_tabs)
        right_col_layout.addWidget(actions_group)
        
        body_layout.addLayout(right_col_layout, 0, 2)

        main_layout.addLayout(body_layout)
        scroll_area.setWidget(main_widget)
        char_info_layout = QVBoxLayout(self.char_info_tab)
        char_info_layout.addWidget(scroll_area)
        self.tabs.addTab(self.char_info_tab, "Character Info")

    def _setup_roleplay_info_tab(self):
        self.roleplay_tab = QWidget()
        layout = QVBoxLayout(self.roleplay_tab)
        form_layout = QFormLayout()
        self.personality_edit = QTextEdit()
        self.ideals_edit = QTextEdit()
        self.bonds_edit = QTextEdit()
        self.flaws_edit = QTextEdit()
        form_layout.addRow("Personality Traits:", self.personality_edit)
        form_layout.addRow("Ideals:", self.ideals_edit)
        form_layout.addRow("Bonds:", self.bonds_edit)
        form_layout.addRow("Flaws:", self.flaws_edit)
        layout.addLayout(form_layout)
        self.allies_edit = QTextEdit()
        layout.addWidget(QLabel("Allies & Organizations"))
        layout.addWidget(self.allies_edit)
        self.backstory_edit = QTextEdit()
        layout.addWidget(QLabel("Character Backstory"))
        layout.addWidget(self.backstory_edit)
        self.tabs.addTab(self.roleplay_tab, "Roleplay Info")

    def _setup_inventory_tab(self):
        self.inventory_widget = InventoryTab()
        self.tabs.addTab(self.inventory_widget, "Inventory")

    def _setup_placeholder_tabs(self):
        self.tabs.addTab(QLabel("Spellbook will go here."), "Spells")
    # endregion

    # region Calculations and Signals
    def _set_dirty(self):
        self.is_dirty = True

    def _connect_signals(self):
        self.main_menu_button.clicked.connect(self._request_return_to_main_menu)
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        
        for widget in self.findChildren(QLineEdit):
            if not widget.isReadOnly():
                widget.textChanged.connect(self._set_dirty)
        for widget in self.findChildren(QSpinBox):
            widget.valueChanged.connect(self._set_dirty)
        for widget in self.findChildren(QCheckBox):
            widget.stateChanged.connect(self._set_dirty)
        for widget in self.findChildren(QTextEdit):
            widget.textChanged.connect(self._set_dirty)
        self.class_combo.currentTextChanged.connect(self._set_dirty)
        
        self.level_spinbox.valueChanged.connect(self._update_all_calculations)
        for spinbox in self.ability_scores.values():
            spinbox.valueChanged.connect(self._update_all_calculations)
        for checkbox in self.save_proficiencies.values():
            checkbox.stateChanged.connect(self._update_all_calculations)
        for checkbox in self.skill_proficiencies.values():
            checkbox.stateChanged.connect(self._update_all_calculations)

    def _update_all_calculations(self):
        level = self.level_spinbox.value()
        prof_bonus = math.ceil(level / 4) + 1
        self.prof_bonus_label.setText(f"+{prof_bonus}")

        for ability, spinbox in self.ability_scores.items():
            score = spinbox.value()
            modifier = math.floor((score - 10) / 2)
            self.ability_modifiers[ability].setText(f"+{modifier}" if modifier >= 0 else str(modifier))

        dex_mod_str = self.ability_modifiers['dexterity'].text()
        self.initiative_edit.setText(dex_mod_str)

        skills_map = {"acrobatics": "dexterity", "animal_handling": "wisdom", "arcana": "intelligence", "athletics": "strength", "deception": "charisma", "history": "intelligence", "insight": "wisdom", "intimidation": "charisma", "investigation": "intelligence", "medicine": "wisdom", "nature": "intelligence", "perception": "wisdom", "performance": "charisma", "persuasion": "charisma", "religion": "intelligence", "sleight_of_hand": "dexterity", "stealth": "dexterity", "survival": "wisdom"}
        
        for ability, checkbox in self.save_proficiencies.items():
            mod = int(self.ability_modifiers[ability].text())
            total = mod + prof_bonus if checkbox.isChecked() else mod
            self.save_values[ability].setText(f"+{total}" if total >= 0 else str(total))

        for skill, checkbox in self.skill_proficiencies.items():
            base_ability = skills_map[skill.replace(" ", "_")]
            mod = int(self.ability_modifiers[base_ability].text())
            total = mod + prof_bonus if checkbox.isChecked() else mod
            self.skill_values[skill].setText(f"+{total}" if total >= 0 else str(total))
        
        class_name = self.class_combo.currentText()
        if class_name in self.class_data:
            class_info = self.class_data[class_name]
            hit_dice = class_info.get("hit_dice", "d6")
            self.hit_dice_total_label.setText(f"{level}{hit_dice}")
            prof_text = "Armor: " + ", ".join(class_info.get("proficiencies", {}).get("armor", []))
            prof_text += "\nWeapons: " + ", ".join(class_info.get("proficiencies", {}).get("weapons", []))
            self.proficiencies_list.setText(prof_text)

    # endregion

    # region Data Handling (Save/Load/Class Change)
    def _request_return_to_main_menu(self):
        if self._check_for_unsaved_changes():
            self.show_main_menu_requested.emit()

    def _new_character(self):
        if self._check_for_unsaved_changes():
            self.current_character_path = None
            self.character_data = {}
            self._populate_sheet_from_data()

    def _gather_character_data(self):
        self.character_data['name'] = self.name_edit.text()
        self.character_data['level'] = self.level_spinbox.value()
        self.character_data['class'] = self.class_combo.currentText()
        self.character_data['race'] = self.race_edit.text()
        self.character_data['background'] = self.background_edit.text()
        self.character_data['alignment'] = self.alignment_edit.text()
        self.character_data['player_name'] = self.player_name_edit.text()
        self.character_data['experience'] = self.exp_spinbox.value()
        self.character_data['inspiration'] = self.inspiration_spinbox.value()
        self.character_data['hp_max'] = self.max_hp_spinbox.value()
        self.character_data['hp_current'] = self.current_hp_spinbox.value()
        self.character_data['hp_temp'] = self.temp_hp_spinbox.value()
        self.character_data['ac'] = self.ac_edit.text()
        self.character_data['speed'] = self.speed_edit.text()
        self.character_data['hit_dice_current'] = self.hit_dice_current_spinbox.value()
        self.character_data['death_saves'] = {
            'successes': [cb.isChecked() for cb in self.death_save_successes],
            'failures': [cb.isChecked() for cb in self.death_save_failures]
        }
        
        self.character_data['ability_scores'] = {k: v.value() for k, v in self.ability_scores.items()}
        self.character_data['proficiencies'] = {
            'saves': [k for k, v in self.save_proficiencies.items() if v.isChecked()],
            'skills': [k for k, v in self.skill_proficiencies.items() if v.isChecked()]
        }
        
        self.character_data['roleplay'] = {
            'personality': self.personality_edit.toPlainText(),
            'ideals': self.ideals_edit.toPlainText(),
            'bonds': self.bonds_edit.toPlainText(),
            'flaws': self.flaws_edit.toPlainText(),
            'allies': self.allies_edit.toPlainText(),
            'backstory': self.backstory_edit.toPlainText()
        }
        
        self.character_data['equipment'] = {name: slot.item_data for name, slot in self.inventory_widget.hexagon_widget.slots.items() if slot.item_data}
        
        inventory = {
            'gear': [self.inventory_widget.gear_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.inventory_widget.gear_list.count())],
            'consumables': [self.inventory_widget.consumables_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.inventory_widget.consumables_list.count())],
            'items': [self.inventory_widget.items_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.inventory_widget.items_list.count())]
        }
        self.character_data['inventory'] = inventory
        
        return self.character_data

    def _populate_sheet_from_data(self):
        data = self.character_data
        
        self.class_combo.blockSignals(True)
        self.name_edit.setText(data.get('name', ''))
        self.level_spinbox.setValue(data.get('level', 1))
        self.class_combo.setCurrentText(data.get('class', ''))
        self.race_edit.setText(data.get('race', ''))
        self.background_edit.setText(data.get('background', ''))
        self.alignment_edit.setText(data.get('alignment', ''))
        self.player_name_edit.setText(data.get('player_name', ''))
        self.exp_spinbox.setValue(data.get('experience', 0))
        self.inspiration_spinbox.setValue(data.get('inspiration', 0))
        self.max_hp_spinbox.setValue(data.get('hp_max', 0))
        self.current_hp_spinbox.setValue(data.get('hp_current', 0))
        self.temp_hp_spinbox.setValue(data.get('hp_temp', 0))
        self.ac_edit.setText(data.get('ac', ''))
        self.speed_edit.setText(data.get('speed', ''))
        self.hit_dice_current_spinbox.setValue(data.get('hit_dice_current', 0))
        self.class_combo.blockSignals(False)

        if 'sprite' in data and data['sprite']:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(data['sprite']))
            self.sprite_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.sprite_label.setText("Click to Upload\nCharacter Sprite")
            self.sprite_label.setPixmap(QPixmap())

        for ability, score in data.get('ability_scores', {}).items():
            if ability in self.ability_scores:
                self.ability_scores[ability].setValue(score)

        self._reset_proficiencies()
        proficiencies = data.get('proficiencies', {})
        for save in proficiencies.get('saves', []):
            if save in self.save_proficiencies:
                self.save_proficiencies[save].setChecked(True)
        for skill in proficiencies.get('skills', []):
            if skill in self.skill_proficiencies:
                self.skill_proficiencies[skill].setChecked(True)
        
        roleplay_data = data.get('roleplay', {})
        self.personality_edit.setPlainText(roleplay_data.get('personality', ''))
        self.ideals_edit.setPlainText(roleplay_data.get('ideals', ''))
        self.bonds_edit.setPlainText(roleplay_data.get('bonds', ''))
        self.flaws_edit.setPlainText(roleplay_data.get('flaws', ''))
        self.allies_edit.setPlainText(roleplay_data.get('allies', ''))
        self.backstory_edit.setPlainText(roleplay_data.get('backstory', ''))
        
        death_saves = data.get('death_saves', {})
        for i, checked in enumerate(death_saves.get('successes', [])):
            self.death_save_successes[i].setChecked(checked)
        for i, checked in enumerate(death_saves.get('failures', [])):
            self.death_save_failures[i].setChecked(checked)
            
        equipment = data.get('equipment', {})
        for name, item_data in equipment.items():
            if name in self.inventory_widget.hexagon_widget.slots:
                slot = self.inventory_widget.hexagon_widget.slots[name]
                slot.item_data = item_data
                slot.setText(item_data['name'])
                slot.setToolTip(format_item_tooltip(item_data))
        
        inventory = data.get('inventory', {})
        self.inventory_widget.gear_list.clear()
        for item_data in inventory.get('gear', []):
            self.inventory_widget._add_item_to_list(item_data)
        self.inventory_widget.consumables_list.clear()
        for item_data in inventory.get('consumables', []):
            self.inventory_widget._add_item_to_list(item_data)
        self.inventory_widget.items_list.clear()
        for item_data in inventory.get('items', []):
            self.inventory_widget._add_item_to_list(item_data)

        self._apply_class_proficiencies(self.class_combo.currentText())
        self._update_all_calculations()
        self.is_dirty = False

    def _on_class_changed(self, class_name):
        if not class_name or class_name not in self.class_data:
            return

        self._reset_proficiencies()
        self._apply_class_proficiencies(class_name)
        
        dialog = ClassChoicesDialog(self)
        dialog.populate_choices(self.class_data[class_name])
        
        if dialog.exec():
            results = dialog.results
            for skill_name in results.get('skills', []):
                key = skill_name.lower().replace(" ", "_")
                if key in self.skill_proficiencies:
                    self.skill_proficiencies[key].setChecked(True)
                    self.skill_proficiencies[key].setEnabled(False)
        self._update_all_calculations()

    def _apply_class_proficiencies(self, class_name):
        if not class_name or class_name not in self.class_data:
            return
        data = self.class_data[class_name]
        for ability in data.get("saving_throws", []):
            if ability in self.save_proficiencies:
                self.save_proficiencies[ability].setChecked(True)
                self.save_proficiencies[ability].setEnabled(False)

    def _upload_sprite(self, event):
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Sprite", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.sprite_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            with open(file_name, "rb") as image_file:
                self.character_data['sprite'] = base64.b64encode(image_file.read()).decode('utf-8')
            self._set_dirty()

    def _save_character(self):
        if self.current_character_path:
            data_to_save = self._gather_character_data()
            with open(self.current_character_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            self.is_dirty = False
            return True
        else:
            return self._save_character_as()

    def _save_character_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Character As", "", "DnD Character (*.dndc);;All Files (*)")
        if file_name:
            if not file_name.endswith('.dndc'):
                file_name += '.dndc'
            self.current_character_path = file_name
            return self._save_character()
        return False

    def _load_character(self):
        if self._check_for_unsaved_changes():
            file_name, _ = QFileDialog.getOpenFileName(self, "Load Character", "", "DnD Character (*.dndc);;All Files (*)")
            if file_name:
                self.current_character_path = file_name
                with open(file_name, 'r') as f:
                    self.character_data = json.load(f)
                self._populate_sheet_from_data()

    def _load_class_data(self):
        plugin_dir = "plugins/core_5e/classes"
        if not os.path.exists(plugin_dir): return
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(plugin_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.class_data[data["name"]] = data

    def _reset_proficiencies(self):
        for checkbox in self.save_proficiencies.values():
            checkbox.setChecked(False)
            checkbox.setEnabled(True)
        for checkbox in self.skill_proficiencies.values():
            checkbox.setChecked(False)
            checkbox.setEnabled(True)
    # endregion
