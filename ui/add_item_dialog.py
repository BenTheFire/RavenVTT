import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLineEdit, QListWidget, 
                             QDialogButtonBox, QFormLayout, QTextEdit, QListWidgetItem)
from PyQt6.QtGui import QPixmap

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Item to Inventory")
        self.setMinimumSize(600, 500)

        self.item_data = {}
        self.selected_item = None

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Browse Tab ---
        browse_widget = QWidget()
        browse_layout = QVBoxLayout(browse_widget)
        
        self.search_bar = QLineEdit(placeholderText="Search for an item...")
        browse_layout.addWidget(self.search_bar)
        
        content_layout = QHBoxLayout()
        self.item_list = QListWidget()
        self.preview_panel = QTextEdit(readOnly=True)
        self.preview_panel.setPlaceholderText("Select an item to see its details...")
        
        content_layout.addWidget(self.item_list, 1)
        content_layout.addWidget(self.preview_panel, 2)
        browse_layout.addLayout(content_layout)
        
        self.tabs.addTab(browse_widget, "Browse Items")

        # --- Custom Tab ---
        custom_widget = QWidget()
        custom_layout = QFormLayout(custom_widget)
        self.custom_name_edit = QLineEdit()
        self.custom_desc_edit = QTextEdit()
        custom_layout.addRow("Item Name:", self.custom_name_edit)
        custom_layout.addRow("Description:", self.custom_desc_edit)
        self.tabs.addTab(custom_widget, "Create Custom Item")

        # --- Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        main_layout.addWidget(self.button_box)

        self._load_items()
        self._connect_signals()

    def _load_items(self):
        plugin_dir = "plugins/core_5e/items"
        for root, _, files in os.walk(plugin_dir):
            for filename in files:
                if filename.endswith(".json"):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        item_id = data.get("id", filename)
                        self.item_data[item_id] = data
                        
                        list_item = QListWidgetItem(data.get("name", item_id))
                        list_item.setData(32, item_id)
                        self.item_list.addItem(list_item)
        self.item_list.sortItems()

    def _connect_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.search_bar.textChanged.connect(self._filter_items)
        self.item_list.itemClicked.connect(self._update_preview_panel)

    def _filter_items(self, text):
        for i in range(self.item_list.count()):
            item = self.item_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _update_preview_panel(self, item_widget):
        item_id = item_widget.data(32)
        data = self.item_data.get(item_id)
        if not data:
            self.preview_panel.setPlainText("Could not find item data.")
            return

        html = ""
        if "image" in data:
            # Assuming image path is relative to the plugin root
            image_path = os.path.join("plugins/core_5e", data["image"])
            if os.path.exists(image_path):
                html += f'<img src="{image_path}" width="100"><br>'

        html += f"<h3>{data.get('name', 'N/A')}</h3>"
        html += f"<i>{data.get('type', '').title()}</i><hr>"
        
        details = []
        for key, value in data.items():
            if key not in ["id", "name", "type", "description", "image"]:
                key_text = key.replace("_", " ").title()
                details.append(f"<b>{key_text}:</b> {value}")
        
        html += "<br>".join(details)
        
        if "description" in data:
            html += f"<br><br><i>{data['description']}</i>"
            
        self.preview_panel.setHtml(html)

    def accept(self):
        if self.tabs.currentIndex() == 0:
            selected_list_item = self.item_list.currentItem()
            if selected_list_item:
                item_id = selected_list_item.data(32)
                self.selected_item = self.item_data.get(item_id)
        else:
            name = self.custom_name_edit.text()
            if name:
                self.selected_item = {
                    "id": f"custom_{name.lower().replace(' ', '_')}",
                    "name": name,
                    "description": self.custom_desc_edit.toPlainText(),
                    "type": "custom"
                }
        
        if self.selected_item:
            super().accept()
