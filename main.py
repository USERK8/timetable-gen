# main.py

import sys
import threading
import multiprocessing

from paths import ensure_user_data
ensure_user_data()

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import theme
from s import SettingsPage
from mc import ManageClasses
from mt import ManageTeachers
from pet import PDFExporterPage
from update import check_for_update


# ── Nav button config: (label, icon_char, slot_attr) ─────────────────────────
NAV_ITEMS = [
    ("Manage Classes",       "◈", "ManageClasses"),
    ("Manage Teachers",      "✦", "manage_teachers_page"),
    ("Generate / Export",    "⬡", "pdf_exporter_page"),
    ("Settings",             "⚙", "settings_page"),
]


class NavButton(QPushButton):
    """Left-sidebar navigation tile."""

    NORMAL = f"""
        QPushButton {{
            background-color: transparent;
            color: {theme.TEXT_SEC};
            border: none;
            border-radius: 12px;
            padding: 14px 20px;
            text-align: left;
            font-size: 15px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {theme.SURFACE2};
            color: {theme.TEXT_PRI};
        }}
    """

    ACTIVE = f"""
        QPushButton {{
            background-color: {theme.ACCENT_DIM};
            color: #ffffff;
            border: none;
            border-left: 3px solid {theme.ACCENT1};
            border-radius: 12px;
            padding: 14px 20px;
            text-align: left;
            font-size: 15px;
            font-weight: 600;
        }}
    """

    def __init__(self, icon, label, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.setStyleSheet(self.NORMAL)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        self.setStyleSheet(self.ACTIVE if active else self.NORMAL)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timetable Gen")
        self.showMaximized()

        # Apply global stylesheet
        QApplication.instance().setStyleSheet(theme.GLOBAL_QSS)

        self._nav_buttons = []

        # Pages
        self.ManageClasses        = ManageClasses(self)
        self.settings_page        = SettingsPage(self)
        self.manage_teachers_page = ManageTeachers(self)
        self.pdf_exporter_page    = PDFExporterPage(self)
        self.home_page            = self._build_home()

        # Stack
        self.stack = QStackedWidget()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.ManageClasses)
        self.stack.addWidget(self.manage_teachers_page)
        self.stack.addWidget(self.pdf_exporter_page)
        self.stack.addWidget(self.settings_page)

        # Root layout: sidebar + stack
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())
        root.addWidget(self.stack, 1)
        self.setLayout(root)

        threading.Thread(target=self._check_update_async, daemon=True).start()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: none;
                border-right: 1px solid {theme.BORDER};
                border-radius: 0px;
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 28, 14, 28)
        layout.setSpacing(6)

        # Logo / app name
        logo = QLabel("⬡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {theme.ACCENT1}; font-size: 36px; padding-bottom: 2px;")
        layout.addWidget(logo)

        app_name = QLabel("Timetable Gen")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(f"""
            color: {theme.TEXT_PRI};
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.5px;
            padding-bottom: 20px;
        """)
        layout.addWidget(app_name)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {theme.BORDER}; margin-bottom: 10px;")
        layout.addWidget(div)

        # Nav items
        page_map = {
            "Manage Classes":    self.ManageClasses,
            "Manage Teachers":   self.manage_teachers_page,
            "Generate / Export": self.pdf_exporter_page,
            "Settings":          self.settings_page,
        }

        for label, icon, _ in NAV_ITEMS:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, lbl=label, pg=page_map[label]: self._nav_to(lbl, pg))
            layout.addWidget(btn)
            self._nav_buttons.append((label, btn))

        layout.addStretch()

        # Home button at bottom
        home_btn = QPushButton("⌂  Home")
        home_btn.setStyleSheet(theme.btn_ghost(padding_v=10, radius=10, font_size=13))
        home_btn.clicked.connect(self.go_home)
        layout.addWidget(home_btn)

        return sidebar

    def _nav_to(self, label, page):
        self.stack.setCurrentWidget(page)
        for lbl, btn in self._nav_buttons:
            btn.set_active(lbl == label)

    # ── Home page ─────────────────────────────────────────────────────────────

    def _build_home(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {theme.BG};")

        outer = QVBoxLayout(page)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(80, 60, 80, 60)
        outer.setSpacing(0)

        # Hero title
        title = QLabel("Timetable Gen")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 56px;
            font-weight: 800;
            color: {theme.ACCENT1};
            letter-spacing: 2px;
            padding-bottom: 6px;
        """)
        outer.addWidget(title)

        sub = QLabel("Smart constraint-based school scheduling")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {theme.TEXT_SEC}; font-size: 15px; padding-bottom: 52px;")
        outer.addWidget(sub)

        # Card grid — 2×2
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QHBoxLayout(grid_widget)
        grid.setSpacing(20)
        grid.setContentsMargins(0, 0, 0, 0)

        cards = [
            ("◈", "Manage Classes",    "Add, edit and organise your class list",           self.ManageClasses),
            ("✦", "Manage Teachers",   "Assign teachers and schedules",                     self.manage_teachers_page),
            ("⬡", "Generate / Export", "Generate timetables and export to Excel",          self.pdf_exporter_page),
            ("⚙", "Settings",          "Help, version info and app details",               self.settings_page),
        ]

        for icon, label, desc, page_ref in cards:
            card = self._home_card(icon, label, desc, page_ref)
            grid.addWidget(card)

        outer.addWidget(grid_widget)
        return page

    def _home_card(self, icon, label, desc, page_ref):
        card = QFrame()
        card.setFixedHeight(200)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.SURFACE};
                border: 1px solid {theme.BORDER};
                border-radius: 18px;
            }}
            QFrame:hover {{
                border: 1px solid {theme.ACCENT1};
                background-color: {theme.SURFACE2};
            }}
        """)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        ic = QLabel(icon)
        ic.setStyleSheet(f"color: {theme.ACCENT1}; font-size: 30px; background: transparent; border: none;")
        lay.addWidget(ic)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {theme.TEXT_PRI}; font-size: 16px; font-weight: 700; background: transparent; border: none;")
        lay.addWidget(lbl)

        dsc = QLabel(desc)
        dsc.setStyleSheet(f"color: {theme.TEXT_SEC}; font-size: 12px; background: transparent; border: none;")
        dsc.setWordWrap(True)
        lay.addWidget(dsc)

        lay.addStretch()

        go = QPushButton("Open →")
        go.setStyleSheet(theme.btn_primary(padding_v=8, radius=10, font_size=12))
        go.clicked.connect(lambda: self.stack.setCurrentWidget(page_ref))
        lay.addWidget(go)

        return card

    # ── Helpers ───────────────────────────────────────────────────────────────

    def go_home(self):
        self.stack.setCurrentWidget(self.home_page)
        for _, btn in self._nav_buttons:
            btn.set_active(False)

    def _check_update_async(self):
        try:
            check_for_update(parent=None)
        except Exception:
            pass

    def resizeEvent(self, event):
        # Guard: __init__ may not have finished yet when the first resize fires
        if not hasattr(self, "ManageClasses"):
            super().resizeEvent(event)
            return
        for page in [self.ManageClasses, self.manage_teachers_page,
                     self.settings_page, self.pdf_exporter_page]:
            if hasattr(page, "dynamic_scaling"):
                page.dynamic_scaling()
        super().resizeEvent(event)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())