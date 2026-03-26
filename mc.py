# mc.py

import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit,
    QMessageBox, QDialog, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import theme
from paths import CLASSES_FILE


def load_classes():
    if not os.path.exists(CLASSES_FILE):
        with open(CLASSES_FILE, "w") as f:
            json.dump([], f)
    with open(CLASSES_FILE, "r") as f:
        return json.load(f)


def save_classes(classes):
    with open(CLASSES_FILE, "w") as f:
        json.dump(classes, f, indent=4)


class EditClassDialog(QDialog):
    def __init__(self, old_name, existing_classes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Class")
        self.setFixedSize(420, 200)
        self.setStyleSheet(theme.dialog_style())

        self.old_name        = old_name
        self.existing_classes = existing_classes
        self.new_name        = None

        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(28, 24, 28, 24)

        lbl = QLabel("Edit class name")
        lbl.setStyleSheet(f"color: {theme.TEXT_SEC}; font-size: 12px;")
        root.addWidget(lbl)

        self.input = QLineEdit(old_name)
        self.input.setStyleSheet(theme.input_style())
        self.input.returnPressed.connect(self.accept_edit)
        root.addWidget(self.input)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(theme.btn_ghost(padding_v=10, radius=10, font_size=13))
        self.cancel_btn.clicked.connect(self.reject)

        self.done_btn = QPushButton("Save")
        self.done_btn.setStyleSheet(theme.btn_primary(padding_v=10, radius=10, font_size=13))
        self.done_btn.clicked.connect(self.accept_edit)

        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.done_btn)
        root.addLayout(btns)

    def accept_edit(self):
        text = self.input.text().strip()
        if not text:
            return
        if text in self.existing_classes and text != self.old_name:
            QMessageBox.warning(self, "Warning", "Class already exists!")
            return
        self.new_name = text
        self.accept()

    def dynamic_scaling(self): pass   # kept for compatibility


class ManageClasses(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.classes = load_classes()
        self._init_ui()
        self.refresh_list()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header row
        header = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet(theme.btn_back())
        self.back_btn.setFixedWidth(100)
        self.back_btn.clicked.connect(self.go_back)
        header.addWidget(self.back_btn)
        header.addStretch()
        root.addLayout(header)

        # Title
        self.title = QLabel("Manage Classes")
        self.title.setStyleSheet(theme.title_style(28))
        root.addWidget(self.title)

        sub = QLabel("Add and manage the classes in your school")
        sub.setStyleSheet(theme.subtitle_style())
        root.addWidget(sub)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(12)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter class name  (e.g. 11A)")
        self.input.setStyleSheet(theme.input_style())
        self.input.setFixedHeight(44)
        self.input.returnPressed.connect(self.add_class)
        input_row.addWidget(self.input)

        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet(theme.btn_primary(padding_v=10, radius=10, font_size=13))
        self.add_btn.setFixedWidth(90)
        self.add_btn.setFixedHeight(44)
        self.add_btn.clicked.connect(self.add_class)
        input_row.addWidget(self.add_btn)
        root.addLayout(input_row)

        # Action buttons
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.edit_btn = QPushButton("✎  Edit Selected")
        self.edit_btn.setStyleSheet(theme.btn_ghost(padding_v=9, radius=10, font_size=13))
        self.edit_btn.clicked.connect(self.edit_class)

        self.delete_btn = QPushButton("✕  Delete Selected")
        self.delete_btn.setStyleSheet(theme.btn_danger(padding_v=9, radius=10, font_size=13))
        self.delete_btn.clicked.connect(self.delete_class)

        action_row.addWidget(self.edit_btn)
        action_row.addWidget(self.delete_btn)
        action_row.addStretch()
        root.addLayout(action_row)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(theme.list_style())
        root.addWidget(self.list_widget)

    def go_back(self):
        if self.parent_window:
            self.parent_window.go_home()

    def refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.classes)

    def add_class(self):
        name = self.input.text().strip()
        if not name:
            return
        if name in self.classes:
            QMessageBox.warning(self, "Warning", "Class already exists!")
            return
        self.classes.append(name)
        save_classes(self.classes)
        self.refresh_list()
        self.input.clear()

    def delete_class(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a class first!")
            return
        del self.classes[row]
        save_classes(self.classes)
        self.refresh_list()

    def edit_class(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a class first!")
            return
        dialog = EditClassDialog(self.classes[row], self.classes, self)
        if dialog.exec():
            self.classes[row] = dialog.new_name
            save_classes(self.classes)
            self.refresh_list()

    def dynamic_scaling(self): pass