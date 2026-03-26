# mt.py

import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QMessageBox, QDialog, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import theme
from paths import TEACH_FILE, CLASSES_FILE, MSC_FILE


def load_teachers():
    if not os.path.exists(TEACH_FILE):
        return []
    with open(TEACH_FILE, "r") as f:
        return json.load(f)


def save_teachers(data):
    with open(TEACH_FILE, "w") as f:
        json.dump(data, f, indent=4)


class EditTeacherDialog(QDialog):
    def __init__(self, teacher_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Teacher")
        self.setFixedSize(420, 240)
        self.setStyleSheet(theme.dialog_style())

        self.teacher_data = teacher_data
        self.result_data  = None

        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(28, 24, 28, 24)

        title = QLabel("Edit Teacher")
        title.setStyleSheet(f"color: {theme.ACCENT1}; font-size: 16px; font-weight: 700;")
        root.addWidget(title)

        lbl_name = QLabel("Teacher Name")
        lbl_name.setStyleSheet(f"color: {theme.TEXT_SEC}; font-size: 11px;")
        root.addWidget(lbl_name)
        self.name_input = QLineEdit(teacher_data["name"])
        self.name_input.setStyleSheet(theme.input_style())
        root.addWidget(self.name_input)

        lbl_sub = QLabel("Subject")
        lbl_sub.setStyleSheet(f"color: {theme.TEXT_SEC}; font-size: 11px;")
        root.addWidget(lbl_sub)
        self.subject_input = QLineEdit(teacher_data["subject"])
        self.subject_input.setStyleSheet(theme.input_style())
        root.addWidget(self.subject_input)

        self.name_input.returnPressed.connect(self.accept_edit)
        self.subject_input.returnPressed.connect(self.accept_edit)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(theme.btn_ghost(padding_v=10, radius=10, font_size=13))
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.setStyleSheet(theme.btn_primary(padding_v=10, radius=10, font_size=13))
        save.clicked.connect(self.accept_edit)
        btns.addWidget(cancel)
        btns.addWidget(save)
        root.addLayout(btns)

    def accept_edit(self):
        name    = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        if not name or not subject:
            return
        self.result_data = {"name": name, "subject": subject}
        self.accept()

    def dynamic_scaling(self): pass


class ManageTeachers(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.teachers      = load_teachers()
        self._init_ui()
        self.refresh_list()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(18)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet(theme.btn_back())
        self.back_btn.setFixedWidth(100)
        self.back_btn.clicked.connect(self.go_back)
        header.addWidget(self.back_btn)
        header.addStretch()
        root.addLayout(header)

        title = QLabel("Manage Teachers")
        title.setStyleSheet(theme.title_style(28))
        root.addWidget(title)

        sub = QLabel("Add teachers, assign subjects and manage their schedules")
        sub.setStyleSheet(theme.subtitle_style())
        root.addWidget(sub)

        # Input row
        inputs = QHBoxLayout()
        inputs.setSpacing(12)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Teacher name")
        self.name_input.setStyleSheet(theme.input_style())
        self.name_input.setFixedHeight(44)
        self.name_input.returnPressed.connect(self.add_teacher)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject")
        self.subject_input.setStyleSheet(theme.input_style())
        self.subject_input.setFixedHeight(44)
        self.subject_input.returnPressed.connect(self.add_teacher)

        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet(theme.btn_primary(padding_v=10, radius=10, font_size=13))
        self.add_btn.setFixedWidth(90)
        self.add_btn.setFixedHeight(44)
        self.add_btn.clicked.connect(self.add_teacher)

        inputs.addWidget(self.name_input, 2)
        inputs.addWidget(self.subject_input, 2)
        inputs.addWidget(self.add_btn)
        root.addLayout(inputs)

        # Action buttons row
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.edit_btn = QPushButton("✎  Edit")
        self.edit_btn.setStyleSheet(theme.btn_ghost(padding_v=9, radius=10, font_size=13))
        self.edit_btn.clicked.connect(self.edit_teacher)

        self.delete_btn = QPushButton("✕  Delete")
        self.delete_btn.setStyleSheet(theme.btn_danger(padding_v=9, radius=10, font_size=13))
        self.delete_btn.clicked.connect(self.delete_teacher)

        self.schedule_btn = QPushButton("📋  Manage Schedule")
        self.schedule_btn.setStyleSheet(theme.btn_ghost(padding_v=9, radius=10, font_size=13))
        self.schedule_btn.clicked.connect(self.manage_schedule)

        self.engagement_btn = QPushButton("📊  Teacher Engagement")
        self.engagement_btn.setStyleSheet(theme.btn_ghost(padding_v=9, radius=10, font_size=13))
        self.engagement_btn.clicked.connect(self.show_engagement)

        actions.addWidget(self.edit_btn)
        actions.addWidget(self.delete_btn)
        actions.addWidget(self.schedule_btn)
        actions.addWidget(self.engagement_btn)
        actions.addStretch()
        root.addLayout(actions)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(theme.list_style())
        root.addWidget(self.list_widget)

    def go_back(self):
        if self.parent_window:
            self.parent_window.go_home()

    def refresh_list(self):
        self.list_widget.clear()
        for t in self.teachers:
            self.list_widget.addItem(f"{t['name']}  ·  {t['subject']}")

    def add_teacher(self):
        name    = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        if not name or not subject:
            return
        for t in self.teachers:
            if t["name"] == name:
                QMessageBox.warning(self, "Warning", "Teacher already exists!")
                return
        self.teachers.append({"name": name, "subject": subject})
        save_teachers(self.teachers)
        self.refresh_list()
        self.name_input.clear()
        self.subject_input.clear()

    def delete_teacher(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a teacher first!")
            return
        del self.teachers[row]
        save_teachers(self.teachers)
        self.refresh_list()

    def edit_teacher(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a teacher first!")
            return
        dialog = EditTeacherDialog(self.teachers[row], self)
        if dialog.exec():
            self.teachers[row] = dialog.result_data
            save_teachers(self.teachers)
            self.refresh_list()

    def manage_schedule(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a teacher first!")
            return
        from mts import ManageTeacherSchedule
        teacher = self.teachers[row]
        self._schedule_window = ManageTeacherSchedule(
            parent=self, teacher_name=teacher["name"], subject=teacher["subject"]
        )
        self._schedule_window.show()
        self._schedule_window.raise_()

    def show_engagement(self):
        from mts import EngagementDialog
        EngagementDialog(self).exec()

    def dynamic_scaling(self): pass