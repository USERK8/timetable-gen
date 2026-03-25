# main.py

import sys
import threading
import multiprocessing

from paths import ensure_user_data
ensure_user_data()   # creates user-dat/ and empty JSON files on first run

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QFont

from s import SettingsPage
from mc import ManageClasses
from mt import ManageTeachers
from pet import PDFExporterPage
from update import check_for_update


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Timetable Gen")
        self.showMaximized()

        self.stack = QStackedWidget()

        # Create pages
        self.ManageClasses         = ManageClasses(self)
        self.settings_page         = SettingsPage(self)
        self.manage_teachers_page  = ManageTeachers(self)
        self.pdf_exporter_page     = PDFExporterPage(self)
        self.home_page             = self.create_home_page()

        # Add pages to stack
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.ManageClasses)
        self.stack.addWidget(self.manage_teachers_page)
        self.stack.addWidget(self.pdf_exporter_page)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.apply_base_style()
        self.dynamic_scaling_home()

        # Check for updates in background — never blocks the UI
        threading.Thread(target=self._check_update_async, daemon=True).start()

    # ---------------- Async update check ----------------
    def _check_update_async(self):
        """Runs on a background thread so startup is never delayed."""
        try:
            check_for_update(parent=None)   # don't pass parent — we're off the main thread
        except Exception:
            pass   # update check failing should never crash the app

    # ---------------- Base style ----------------
    def apply_base_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
            }

            QFrame {
                background-color: #1c1c1c;
                border: 3px solid #2a2a2a;
                border-radius: 20px;
            }

            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #0f3d2e,
                    stop:1 #1b2a4a
                );
                color: white;
                border: 2px solid #2f2f2f;
                border-radius: 15px;
            }

            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #145c43,
                    stop:1 #243b6b
                );
            }
        """)

    # ---------------- Home page ----------------
    def create_home_page(self):
        page = QWidget()
        self.home_layout = QVBoxLayout()
        self.home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.home_layout.setSpacing(30)
        self.home_layout.setContentsMargins(60, 40, 60, 40)

        # Title
        self.title = QLabel("Timetable Gen")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button container
        self.button_box = QFrame()
        self.box_layout = QVBoxLayout()
        self.box_layout.setSpacing(25)

        # Buttons
        self.buttons = []

        btn_manage_classes   = QPushButton("Manage Classes")
        btn_manage_teachers  = QPushButton("Manage Teachers")
        btn_generate         = QPushButton("Select the Excel Exporter Type")
        btn_settings         = QPushButton("Settings")

        btn_manage_classes.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.ManageClasses)
        )
        btn_manage_teachers.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.manage_teachers_page)
        )
        btn_settings.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.settings_page)
        )
        btn_generate.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.pdf_exporter_page)
        )

        self.buttons.extend([
            btn_manage_classes,
            btn_manage_teachers,
            btn_generate,
            btn_settings
        ])

        for btn in self.buttons:
            self.box_layout.addWidget(btn)

        self.button_box.setLayout(self.box_layout)

        self.home_layout.addWidget(self.title)
        self.home_layout.addWidget(self.button_box)

        page.setLayout(self.home_layout)
        return page

    # ---------------- Dynamic scaling ----------------
    def resizeEvent(self, event):
        self.dynamic_scaling_home()
        if hasattr(self, "ManageClasses") and hasattr(self.ManageClasses, "dynamic_scaling"):
            self.ManageClasses.dynamic_scaling()
        if hasattr(self, "manage_teachers_page") and hasattr(self.manage_teachers_page, "dynamic_scaling"):
            self.manage_teachers_page.dynamic_scaling()
        if hasattr(self, "settings_page") and hasattr(self.settings_page, "dynamic_scaling"):
            self.settings_page.dynamic_scaling()
        if hasattr(self, "pdf_exporter_page") and hasattr(self.pdf_exporter_page, "dynamic_scaling"):
            self.pdf_exporter_page.dynamic_scaling()
        super().resizeEvent(event)

    def dynamic_scaling_home(self):
        if not hasattr(self, "title"):
            return

        width = self.width()

        title_size = max(40, width // 20)
        self.title.setFont(QFont("Arial", title_size, QFont.Weight.Bold))
        self.title.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #ff4ecd,
                    stop:1 #a855f7
                );
                margin-bottom: 50px;
            }
        """)

        button_font_size = max(18, width // 60)
        padding          = max(15, width // 120)

        for btn in self.buttons:
            btn.setFont(QFont("Arial", button_font_size))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(
                        x1:0, y1:0,
                        x2:1, y2:1,
                        stop:0 #0f3d2e,
                        stop:1 #1b2a4a
                    );
                    color: white;
                    border: 2px solid #2f2f2f;
                    border-radius: 20px;
                    padding: {padding}px;
                }}

                QPushButton:hover {{
                    background-color: qlineargradient(
                        x1:0, y1:0,
                        x2:1, y2:1,
                        stop:0 #145c43,
                        stop:1 #243b6b
                    );
                }}
            """)

    def go_home(self):
        self.stack.setCurrentWidget(self.home_page)


# -------------------------------------------------------
# ENTRY POINT
# multiprocessing.freeze_support() is required on Windows
# when the app is bundled (e.g. with PyInstaller).
# The `if __name__ == "__main__"` guard is required for
# multiprocessing to work correctly on Windows — without it,
# spawning a worker process recursively re-runs the whole
# script and crashes.
# -------------------------------------------------------

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())