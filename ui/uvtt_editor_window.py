import math
from PyQt6.QtCore import pyqtSignal, Qt, QRectF, QLineF
from PyQt6.QtGui import QAction, QPixmap, QActionGroup, QPen, QColor, QCursor
from PyQt6.QtWidgets import (QWidget, QMenu, QToolBar, QGraphicsView, QGraphicsScene, 
                             QVBoxLayout, QFileDialog, QLabel, QSpinBox, QComboBox, QPushButton, QColorDialog)


class EnhancedGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self._panning = False
        self._pan_start_pos = None
        self.panning_enabled = True

        self._grid_visible = False
        self._grid_size = 50
        self._grid_type = 'Square'
        self._grid_pen = QPen(QColor(0, 0, 0, 125), 1)

    def set_panning(self, enabled):
        self.panning_enabled = enabled

    def mousePressEvent(self, event):
        if self.panning_enabled and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_start_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def set_grid_visible(self, visible):
        self._grid_visible = visible
        self.viewport().update()

    def set_grid_size(self, size):
        self._grid_size = max(1, size)
        self.viewport().update()

    def set_grid_type(self, grid_type):
        self._grid_type = grid_type
        self.viewport().update()

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.25 if event.angleDelta().y() > 0 else 1 / 1.25
            self.scale(zoom_factor, zoom_factor)
        else:
            super().wheelEvent(event)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        if not self._grid_visible or self._grid_size <= 0:
            return

        painter.setPen(self._grid_pen)
        view_rect = self.mapToScene(self.viewport().geometry()).boundingRect()

        if self._grid_type == 'Square':
            self._draw_square_grid(painter, view_rect)
        elif self._grid_type == 'Hex':
            self._draw_hex_grid(painter, view_rect)

    def _draw_square_grid(self, painter, rect):
        left = int(rect.left() / self._grid_size) * self._grid_size
        top = int(rect.top() / self._grid_size) * self._grid_size
        
        lines = []
        x = left
        while x < rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size
        
        y = top
        while y < rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size
            
        painter.drawLines(lines)

    def _draw_hex_grid(self, painter, rect):
        self._draw_square_grid(painter, rect)


class UvttEditorWindow(QWidget):
    show_main_menu_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.scene = QGraphicsScene()
        self.view = EnhancedGraphicsView(self.scene)
        layout.addWidget(self.view)
        
        self._create_menus()
        self._create_main_toolbar()
        self._create_context_toolbars()
        self._create_grid_toolbar()

    def _create_menus(self):
        self.file_menu = QMenu("&File", self)
        self.edit_menu = QMenu("&Edit", self)

        main_menu_action = QAction("Main Menu", self)
        main_menu_action.triggered.connect(self.show_main_menu_requested.emit)
        self.file_menu.addAction(main_menu_action)
        self.file_menu.addSeparator()

        import_action = QAction("&Import Image", self)
        import_action.triggered.connect(self._import_image)
        self.file_menu.addAction(import_action)

        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        self.edit_menu.addActions([undo_action, redo_action])

    def _create_main_toolbar(self):
        self.toolbar = QToolBar("Tools")
        self.main_tool_group = QActionGroup(self)
        self.main_tool_group.setExclusive(True)
        
        sel_action = self._create_tool_action("SEL", "Select", True)
        sel_action.setChecked(True)
        mea_action = self._create_tool_action("MEA", "Measurement", True)
        self.toolbar.addActions([sel_action, mea_action])
        self.toolbar.addSeparator()

        drw_action = self._create_tool_action("DRW", "Drawing Tools", True)
        fow_action = self._create_tool_action("FOW", "Fog of War Tools", True)
        vbl_action = self._create_tool_action("VBL", "Vision Blocking Tools", True)
        self.toolbar.addActions([drw_action, fow_action, vbl_action])

    def _create_context_toolbars(self):
        self.drawing_toolbar = QToolBar("Drawing")
        self.drawing_toolbar.addActions([QAction("Pencil", self), QAction("Line", self), QAction("Square", self), QAction("Circle", self)])
        self.color_button = QPushButton("Color")
        self.color_button.clicked.connect(lambda: QColorDialog.getColor())
        self.drawing_toolbar.addWidget(self.color_button)
        self.drawing_toolbar.setVisible(False)

        self.fow_toolbar = QToolBar("Fog of War")
        fow_mode_group = QActionGroup(self)
        fow_mode_group.setExclusive(True)
        
        cover_action = QAction("Cover", self, checkable=True)
        cover_action.setChecked(True)
        reveal_action = QAction("Reveal", self, checkable=True)
        
        fow_mode_group.addAction(cover_action)
        fow_mode_group.addAction(reveal_action)
        
        self.fow_toolbar.addActions([QAction("Square", self), QAction("Circle", self), QAction("Polygon", self)])
        self.fow_toolbar.addSeparator()
        self.fow_toolbar.addActions([cover_action, reveal_action])
        self.fow_toolbar.setVisible(False)

        self.vbl_toolbar = QToolBar("Vision Blocking")
        self.vbl_toolbar.addActions([QAction("Square", self), QAction("Hollow Square", self), QAction("Circle", self), QAction("Hollow Circle", self), QAction("Line", self), QAction("Polygon", self)])
        self.vbl_type_combo = QComboBox()
        self.vbl_type_combo.addItems(["Wall", "Hill", "Pit"])
        self.vbl_toolbar.addWidget(self.vbl_type_combo)
        self.vbl_toolbar.setVisible(False)

        self.context_toolbars = {"DRW": self.drawing_toolbar, "FOW": self.fow_toolbar, "VBL": self.vbl_toolbar}

    def _create_grid_toolbar(self):
        self.grid_toolbar = QToolBar("Grid")
        
        grid_visible_action = QAction("Grid", self, checkable=True)
        grid_visible_action.toggled.connect(self.view.set_grid_visible)
        self.grid_toolbar.addAction(grid_visible_action)
        
        self.grid_size_label = QLabel(" Size: ")
        self.grid_toolbar.addWidget(self.grid_size_label)
        self.size_spinbox = QSpinBox(minimum=10, maximum=500, value=50)
        self.size_spinbox.valueChanged.connect(self.view.set_grid_size)
        self.grid_toolbar.addWidget(self.size_spinbox)

        self.grid_type_label = QLabel(" Type: ")
        self.grid_toolbar.addWidget(self.grid_type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Square", "Hex"])
        self.type_combo.currentTextChanged.connect(self.view.set_grid_type)
        self.grid_toolbar.addWidget(self.type_combo)

    def _create_tool_action(self, text, tooltip, is_checkable):
        action = QAction(text, self)
        action.setToolTip(tooltip)
        action.setCheckable(is_checkable)
        action.triggered.connect(self.on_main_tool_selected)
        self.main_tool_group.addAction(action)
        return action

    def on_main_tool_selected(self):
        checked_action = self.main_tool_group.checkedAction()
        if not checked_action:
            for toolbar in self.context_toolbars.values():
                toolbar.setVisible(False)
            return
        
        tool_name = checked_action.text()
        self.view.set_panning(tool_name == "SEL")

        for name, toolbar in self.context_toolbars.items():
            toolbar.setVisible(name == tool_name)

    def _import_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.scene.clear()
            pixmap = QPixmap(file_name)
            self.scene.addPixmap(pixmap)
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
