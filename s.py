# s.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import theme
from paths import VERSION_FILE


class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet(theme.btn_back())
        self.back_btn.setFixedWidth(100)
        self.back_btn.clicked.connect(self.main_window.go_home)
        header.addWidget(self.back_btn)
        header.addStretch()
        root.addLayout(header)

        title = QLabel("Settings")
        title.setStyleSheet(theme.title_style(28))
        root.addWidget(title)

        sub = QLabel("App info, help and version details")
        sub.setStyleSheet(theme.subtitle_style())
        root.addWidget(sub)

        # Settings cards
        cards_data = [
            ("?", "Help",         "Get support or contact the developer",  self.show_help),
            ("i", "About",        "About this app and its creator",         self.show_about),
            ("◎", "Version",      "Check the current installed version",    self.show_version),
        ]

        for icon, label, desc, fn in cards_data:
            root.addWidget(self._setting_row(icon, label, desc, fn))

        root.addStretch()

    def _setting_row(self, icon, label, desc, fn):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: 1px solid {theme.BORDER};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border-color: {theme.BORDER_GLOW};
            }}
        """)
        card.setFixedHeight(76)

        row = QHBoxLayout(card)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(16)

        ic = QLabel(icon)
        ic.setFixedWidth(32)
        ic.setStyleSheet(f"color: {theme.ACCENT1}; font-size: 20px; font-weight: bold; background: transparent; border: none;")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(ic)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {theme.TEXT_PRI}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        dsc = QLabel(desc)
        dsc.setStyleSheet(f"color: {theme.TEXT_SEC}; font-size: 11px; background: transparent; border: none;")
        text_col.addWidget(lbl)
        text_col.addWidget(dsc)
        row.addLayout(text_col)

        row.addStretch()

        btn = QPushButton("Open")
        btn.setFixedWidth(80)
        btn.setFixedHeight(36)
        btn.setStyleSheet(theme.btn_ghost(padding_v=6, radius=8, font_size=12))
        btn.clicked.connect(fn)
        row.addWidget(btn)

        return card

    def show_help(self):
        QMessageBox.information(
            self, "Help",
            "Facing trouble?\n\nContact us:\nEmail: userk8.dev@gmail.com"
        )

    def show_about(self):
        QMessageBox.information(
            self, "About",
            "Timetable Gen\n\nDeveloped by P. Sohan Kumar Reddy\nClass 11A  ·  Batch 2025–26"
        )

    def show_version(self):
        try:
            with open(VERSION_FILE, "r") as f:
                version = f.read().strip()
        except FileNotFoundError:
            version = "Version file not found."
        QMessageBox.information(self, "Version", f"Current Version: {version}")

    def dynamic_scaling(self): pass
    def showEvent(self, event):
        super().showEvent(event)