import math
import json
from PyQt6.QtCore import Qt, QPointF, QMimeData
from PyQt6.QtGui import QPainter, QPolygonF, QPen, QColor, QDrag, QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QGridLayout, 
                             QPushButton, QListWidget, QListWidgetItem, QApplication, QDialog, QTextBrowser)
from ui.add_item_dialog import AddItemDialog

def format_item_tooltip(item_data):
    if not item_data:
        return ""
    html = f"<h3>{item_data.get('name', 'N/A')}</h3>"
    html += f"<i>{item_data.get('type', '').title()}</i><hr>"
    details = []
    for key, value in item_data.items():
        if key not in ["id", "name", "type", "description"]:
            key_text = key.replace("_", " ").title()
            details.append(f"<b>{key_text}:</b> {value}")
    html += "<br>".join(details)
    if "description" in item_data:
        html += f"<br><br><i>{item_data['description']}</i>"
    return html

class ItemDetailDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(item_data.get("name", "Item Details"))
        self.setMinimumSize(300, 200)
        layout = QVBoxLayout(self)
        text_browser = QTextBrowser()
        text_browser.setHtml(format_item_tooltip(item_data))
        layout.addWidget(text_browser)

class DroppableSlot(QLabel):
    def __init__(self, slot_type, text, inventory_tab, parent=None):
        super().__init__(text, parent)
        self.slot_type = slot_type
        self.inventory_tab = inventory_tab
        self.item_data = None
        self.setAcceptDrops(True)
        self.setFixedSize(80, 40)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid grey; background-color: rgba(255, 255, 255, 150);")

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/json"):
            item_data = json.loads(event.mimeData().data("application/json").data().decode())
            item_slot = item_data.get("slot")
            
            if isinstance(item_slot, list) and self.slot_type in item_slot:
                event.acceptProposedAction()
            elif item_slot == self.slot_type:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        item_data = json.loads(event.mimeData().data("application/json").data().decode())
        
        if self.item_data:
            self.inventory_tab.unequip_item(self.item_data)
            
        self.item_data = item_data
        self.setText(item_data["name"])
        self.setToolTip(format_item_tooltip(item_data))
        self.inventory_tab.mark_item_as_equipped(item_data["id"])
        event.acceptProposedAction()

    def mouseDoubleClickEvent(self, event):
        if self.item_data:
            self.inventory_tab.unequip_item(self.item_data)
            self.item_data = None
            self.setText(self.slot_type.replace("_", " ").title())
            self.setToolTip("")

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.itemDoubleClicked.connect(self.show_item_details)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            item_data = item.data(Qt.ItemDataRole.UserRole)
            mime_data = QMimeData()
            mime_data.setData("application/json", json.dumps(item_data).encode())
            
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.CopyAction)

    def show_item_details(self, item):
        item_data = item.data(Qt.ItemDataRole.UserRole)
        if item_data:
            dialog = ItemDetailDialog(item_data, self)
            dialog.exec()

class HexagonWidget(QWidget):
    def __init__(self, inventory_tab, parent=None):
        super().__init__(parent)
        self.inventory_tab = inventory_tab
        self.setMinimumSize(300, 300)
        self.slots = {}
        self._create_slots()

    def _create_slots(self):
        slot_map = {
            "Head": "head", "Right Hand": "right_hand", "Cape": "cape",
            "Boots": "boots", "Belt": "belt", "Left Hand": "left_hand", "Armor": "armor"
        }
        for name, slot_type in slot_map.items():
            slot = DroppableSlot(slot_type, name, self.inventory_tab)
            slot.setParent(self)
            self.slots[name] = slot

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(180, 180, 180), 2)
        painter.setPen(pen)
        center_x, center_y = self.width() / 2, self.height() / 2
        size = min(center_x, center_y) * 0.8
        points = [QPointF(center_x + size * math.cos(math.pi / 3 * i), center_y + size * math.sin(math.pi / 3 * i)) for i in range(6)]
        painter.drawPolygon(QPolygonF(points))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        center_x, center_y = self.width() / 2, self.height() / 2
        size = min(center_x, center_y) * 0.8
        
        armor_slot = self.slots["Armor"]
        armor_slot.move(int(center_x - armor_slot.width() / 2), int(center_y - armor_slot.height() / 2))

        slot_positions = {"Head": 0, "Right Hand": 1, "Cape": 2, "Boots": 3, "Belt": 4, "Left Hand": 5}
        for name, index in slot_positions.items():
            slot = self.slots[name]
            angle = math.pi / 3 * index - (math.pi / 2)
            x = center_x + size * math.cos(angle) - slot.width() / 2
            y = center_y + size * math.sin(angle) - slot.height() / 2
            slot.move(int(x), int(y))

class InventoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        
        self.hexagon_widget = HexagonWidget(self)
        main_layout.addWidget(self.hexagon_widget)
        
        self.inventory_tabs = QTabWidget()
        
        self.gear_list = DraggableListWidget()
        self.consumables_list = QListWidget()
        self.items_list = QListWidget()
        
        self.inventory_tabs.addTab(self.gear_list, "Gear")
        self.inventory_tabs.addTab(self.consumables_list, "Consumables")
        self.inventory_tabs.addTab(self.items_list, "Items")
        
        main_layout.addWidget(self.inventory_tabs)
        
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self._open_add_item_dialog)
        main_layout.addWidget(self.add_item_button)

    def _open_add_item_dialog(self):
        dialog = AddItemDialog(self)
        if dialog.exec():
            item_data = dialog.selected_item
            if item_data:
                self._add_item_to_list(item_data)

    def _add_item_to_list(self, item_data, is_equipped=False):
        list_item = QListWidgetItem(item_data["name"])
        list_item.setData(Qt.ItemDataRole.UserRole, item_data)
        list_item.setToolTip(format_item_tooltip(item_data))
        
        if is_equipped:
            font = list_item.font()
            font.setBold(True)
            font.setItalic(True)
            list_item.setFont(font)
            list_item.setForeground(QColor('grey'))
        
        item_type = item_data.get("type", "custom")
        if item_type in ["armor", "weapon", "accessory"]:
            self.gear_list.addItem(list_item)
        elif item_type == "consumable":
            self.consumables_list.addItem(list_item)
        else:
            self.items_list.addItem(list_item)

    def find_item_in_list(self, item_id):
        for i in range(self.gear_list.count()):
            item = self.gear_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole)["id"] == item_id:
                return item
        return None

    def mark_item_as_equipped(self, item_id):
        item = self.find_item_in_list(item_id)
        if item:
            font = item.font()
            font.setBold(True)
            font.setItalic(True)
            item.setFont(font)
            item.setForeground(QColor('grey'))

    def unequip_item(self, item_data):
        if not item_data:
            return
        item = self.find_item_in_list(item_data["id"])
        if item:
            font = item.font()
            font.setBold(False)
            font.setItalic(False)
            item.setFont(font)
            item.setForeground(QApplication.palette().color(QApplication.palette().ColorRole.Text))
        else:
            self._add_item_to_list(item_data, is_equipped=False)
