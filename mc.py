import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit,
    QMessageBox, QDialog, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        self.setFixedSize(400, 180)

        self.old_name = old_name
        self.existing_classes = existing_classes
        self.new_name = None

        layout = QVBoxLayout()
        layout.setSpacing(8)

        self.label = QLabel("Edit Class Name:")
        layout.addWidget(self.label)

        self.input = QLineEdit(old_name)
        self.input.returnPressed.connect(self.accept_edit)
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        self.done_btn = QPushButton("Done")
        self.done_btn.clicked.connect(self.accept_edit)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.done_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Initial scaling
        self.dynamic_scaling()

    def accept_edit(self):
        text = self.input.text().strip()
        if not text:
            return
        if text in self.existing_classes and text != self.old_name:
            QMessageBox.warning(self, "Warning", "Class already exists!")
            return
        self.new_name = text
        self.accept()

    def dynamic_scaling(self):
        width = self.width()
        for lbl in [self.label]:
            lbl.setFont(QFont("Arial", max(10, width // 40)))
        self.input.setFont(QFont("Arial", max(10, width // 45)))
        for btn in [self.done_btn, self.cancel_btn]:
            btn.setFont(QFont("Arial", max(10, width // 45)))
            btn.setStyleSheet(f"""
                QPushButton {{
                    padding: 6px 12px;
                    border-radius: 12px;
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f3d2e, stop:1 #1b2a4a
                    );
                    color: white;
                    border: 1px solid #2f2f2f;
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #145c43, stop:1 #243b6b
                    );
                }}
            """)


class ManageClasses(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.classes = load_classes()
        self.init_ui()
        self.refresh_list()
        self.dynamic_scaling()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(50, 40, 50, 40)

        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_btn)

        self.title = QLabel("Manage Classes")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter class (e.g., 11A)")
        self.input.returnPressed.connect(self.add_class)
        self.layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        self.add_btn.clicked.connect(self.add_class)
        self.edit_btn.clicked.connect(self.edit_class)
        self.delete_btn.clicked.connect(self.delete_class)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

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
        dialog.dynamic_scaling()
        if dialog.exec():
            self.classes[row] = dialog.new_name
            save_classes(self.classes)
            self.refresh_list()

    def dynamic_scaling(self):
        width = self.parent_window.width() if self.parent_window else self.width()

        # Smaller, readable fonts
        self.title.setFont(QFont("Arial", max(16, width // 50)))
        self.back_btn.setFont(QFont("Arial", max(12, width // 60)))
        self.input.setFont(QFont("Arial", max(12, width // 60)))
        for btn in [self.add_btn, self.edit_btn, self.delete_btn]:
            btn.setFont(QFont("Arial", max(12, width // 60)))
        self.list_widget.setFont(QFont("Arial", max(12, width // 60)))