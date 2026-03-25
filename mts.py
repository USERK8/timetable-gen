import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QCheckBox, QInputDialog
)
from PyQt6.QtCore import Qt

from paths import MSC_FILE, CLASSES_FILE


def load_classes():
    if not os.path.exists(CLASSES_FILE):
        return []
    with open(CLASSES_FILE, "r") as f:
        return json.load(f)


def load_msc():
    if not os.path.exists(MSC_FILE):
        with open(MSC_FILE, "w") as f:
            json.dump({}, f)
    with open(MSC_FILE, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}  # Ensure data is a dict
        except json.JSONDecodeError:
            data = {}  # Fix if file is empty or invalid
    return data


def save_msc(data):
    with open(MSC_FILE, "w") as f:
        json.dump(data, f, indent=4)


class ManageTeacherSchedule(QDialog):
    def __init__(self, teacher_name, subject, parent=None):
        super().__init__(parent)

        self.teacher_name = teacher_name
        self.subject = subject

        self.setWindowTitle("Manage Teacher Schedule")
        self.resize(400, 500)

        self.layout = QVBoxLayout()

        title = QLabel(f"Manage {teacher_name}'s Schedule")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self.classes = load_classes()
        self.checkboxes = []

        # Load existing schedule for this teacher
        self.msc_data = load_msc()
        teacher_classes = self.msc_data.get(self.teacher_name, {}).get("classes", {})

        for cls in self.classes:
            checkbox = QCheckBox(cls)
            if cls in teacher_classes:
                checkbox.setChecked(True)  # Auto-check existing assigned classes
            checkbox.stateChanged.connect(self.class_checked)
            self.layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        self.setLayout(self.layout)

    def class_checked(self, state):
        checkbox = self.sender()
        if state == Qt.CheckState.Checked.value:
            periods, ok = QInputDialog.getInt(
                self,
                "Enter Periods",
                f"Number of {self.subject} periods per week:",
                1, 1, 48
            )

            if ok:
                self.save_data(checkbox.text(), periods)
            else:
                checkbox.setChecked(False)
        else:
            # If unchecked, remove the class from teacher
            self.remove_class(checkbox.text())

    def save_data(self, class_name, periods):
        data = load_msc()

        if self.teacher_name not in data:
            data[self.teacher_name] = {
                "subject": self.subject,
                "classes": {}
            }

        data[self.teacher_name]["classes"][class_name] = periods
        save_msc(data)

    def remove_class(self, class_name):
        data = load_msc()
        if self.teacher_name in data and class_name in data[self.teacher_name]["classes"]:
            del data[self.teacher_name]["classes"][class_name]
            save_msc(data)