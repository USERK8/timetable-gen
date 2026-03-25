import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QMessageBox, QDialog, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from paths import TEACH_FILE, CLASSES_FILE, MSC_FILE


# ------------------- Load / Save -------------------
def load_teachers():
    if not os.path.exists(TEACH_FILE):
        return []
    with open(TEACH_FILE, "r") as f:
        return json.load(f)


def save_teachers(data):
    with open(TEACH_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ------------------- Edit Teacher Dialog -------------------
class EditTeacherDialog(QDialog):
    def __init__(self, teacher_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Teacher")
        self.setFixedSize(400, 200)

        self.teacher_data = teacher_data
        self.result_data = None

        layout = QVBoxLayout()
        layout.setSpacing(8)

        self.label_name = QLabel("Teacher Name:")
        layout.addWidget(self.label_name)
        self.name_input = QLineEdit()
        self.name_input.setText(teacher_data["name"])
        layout.addWidget(self.name_input)

        self.label_subject = QLabel("Subject:")
        layout.addWidget(self.label_subject)
        self.subject_input = QLineEdit()
        self.subject_input.setText(teacher_data["subject"])
        layout.addWidget(self.subject_input)

        btn_layout = QHBoxLayout()
        self.done_btn = QPushButton("Done")
        self.done_btn.clicked.connect(self.accept_edit)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.done_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.name_input.returnPressed.connect(self.accept_edit)
        self.subject_input.returnPressed.connect(self.accept_edit)

        self.dynamic_scaling()

    def accept_edit(self):
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        if not name or not subject:
            return
        self.result_data = {"name": name, "subject": subject}
        self.accept()

    def dynamic_scaling(self):
        width = self.width()
        # Reasonable smaller font sizes
        for lbl in [self.label_name, self.label_subject]:
            lbl.setFont(QFont("Arial", max(10, width // 40)))
        for inp in [self.name_input, self.subject_input]:
            inp.setFont(QFont("Arial", max(10, width // 45)))
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


# ------------------- Manage Teachers Page -------------------
class ManageTeachers(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.teachers = load_teachers()
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

        self.title = QLabel("Manage Teachers")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Teacher Name")
        self.layout.addWidget(self.name_input)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject")
        self.layout.addWidget(self.subject_input)

        self.name_input.returnPressed.connect(self.add_teacher)
        self.subject_input.returnPressed.connect(self.add_teacher)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.schedule_btn = QPushButton("Manage Teacher's Schedule")

        self.add_btn.clicked.connect(self.add_teacher)
        self.edit_btn.clicked.connect(self.edit_teacher)
        self.delete_btn.clicked.connect(self.delete_teacher)
        self.schedule_btn.clicked.connect(self.manage_schedule)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.schedule_btn)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

    def go_back(self):
        if self.parent_window:
            self.parent_window.go_home()

    def refresh_list(self):
        self.list_widget.clear()
        for teacher in self.teachers:
            self.list_widget.addItem(f"{teacher['name']} — {teacher['subject']}")

    def add_teacher(self):
        name = self.name_input.text().strip()
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
        dialog.dynamic_scaling()
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

    def dynamic_scaling(self):
        width = self.parent_window.width() if self.parent_window else self.width()

        # Reasonable smaller fonts
        self.title.setFont(QFont("Arial", max(16, width // 50)))
        self.back_btn.setFont(QFont("Arial", max(12, width // 60)))
        self.name_input.setFont(QFont("Arial", max(12, width // 60)))
        self.subject_input.setFont(QFont("Arial", max(12, width // 60)))
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.schedule_btn]:
            btn.setFont(QFont("Arial", max(12, width // 60)))
        self.list_widget.setFont(QFont("Arial", max(12, width // 60)))