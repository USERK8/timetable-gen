# theme.py
# Central design system — Midnight Glass theme
# Import this in every UI file instead of hardcoding colours.

# ── Palette ───────────────────────────────────────────────────────────────────

BG          = "#09090f"          # near-black base
SURFACE     = "#10101a"          # card / page surface
SURFACE2    = "#16162a"          # elevated surface (list, input bg)
BORDER      = "#1e1e38"          # default border
BORDER_GLOW = "#2d2d5e"          # border on focus / hover

ACCENT1     = "#7c5cfc"          # violet  (primary accent)
ACCENT2     = "#00d4ff"          # cyan    (secondary accent)
ACCENT_DIM  = "#3d2e8a"          # dimmed violet for pressed states

TEXT_PRI    = "#e8e8f0"          # primary text
TEXT_SEC    = "#7b7b9a"          # secondary / muted text
TEXT_HINT   = "#44445a"          # placeholder / hint

SUCCESS     = "#22c55e"
WARNING     = "#f59e0b"
DANGER      = "#ef4444"

# ── Global stylesheet (applied once to QApplication or MainWindow) ────────────

GLOBAL_QSS = f"""
    * {{
        font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    }}

    QWidget {{
        background-color: {BG};
        color: {TEXT_PRI};
    }}

    QStackedWidget {{
        background-color: {BG};
    }}

    /* ── Scrollbars ── */
    QScrollBar:vertical {{
        background: {SURFACE};
        width: 8px;
        border-radius: 4px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER_GLOW};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {ACCENT1};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {SURFACE};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER_GLOW};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {ACCENT1};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ── MessageBox ── */
    QMessageBox {{
        background-color: {SURFACE};
        color: {TEXT_PRI};
    }}
    QMessageBox QLabel {{
        color: {TEXT_PRI};
        font-size: 13px;
    }}
    QMessageBox QPushButton {{
        background-color: {ACCENT_DIM};
        color: {TEXT_PRI};
        border: 1px solid {ACCENT1};
        border-radius: 8px;
        padding: 6px 20px;
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {ACCENT1};
    }}
"""


# ── Reusable style builders ────────────────────────────────────────────────────

def page_style():
    return f"background-color: {BG};"


def card_style(radius=18):
    return f"""
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: {radius}px;
    """


def title_style(size=32):
    """Gradient violet→cyan title label."""
    return f"""
        QLabel {{
            font-size: {size}px;
            font-weight: 700;
            color: {ACCENT1};
            letter-spacing: 1px;
            padding-bottom: 8px;
        }}
    """


def subtitle_style(size=13):
    return f"color: {TEXT_SEC}; font-size: {size}px;"


def btn_primary(padding_v=14, padding_h=0, radius=14, font_size=15):
    """Filled accent button."""
    return f"""
        QPushButton {{
            background-color: {ACCENT1};
            color: #ffffff;
            border: none;
            border-radius: {radius}px;
            padding: {padding_v}px {padding_h}px;
            font-size: {font_size}px;
            font-weight: 600;
            letter-spacing: 0.4px;
        }}
        QPushButton:hover {{
            background-color: #9370ff;
        }}
        QPushButton:pressed {{
            background-color: {ACCENT_DIM};
        }}
        QPushButton:disabled {{
            background-color: {BORDER};
            color: {TEXT_HINT};
        }}
    """


def btn_ghost(padding_v=14, padding_h=0, radius=14, font_size=15):
    """Outline-only ghost button."""
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {ACCENT1};
            border: 1px solid {ACCENT1};
            border-radius: {radius}px;
            padding: {padding_v}px {padding_h}px;
            font-size: {font_size}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_DIM};
            color: #fff;
        }}
        QPushButton:pressed {{
            background-color: {ACCENT1};
            color: #fff;
        }}
        QPushButton:disabled {{
            border-color: {BORDER};
            color: {TEXT_HINT};
        }}
    """


def btn_danger(padding_v=12, padding_h=0, radius=12, font_size=14):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {DANGER};
            border: 1px solid {DANGER};
            border-radius: {radius}px;
            padding: {padding_v}px {padding_h}px;
            font-size: {font_size}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {DANGER};
            color: #fff;
        }}
    """


def btn_back(font_size=13):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {TEXT_SEC};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 7px 18px;
            font-size: {font_size}px;
        }}
        QPushButton:hover {{
            color: {TEXT_PRI};
            border-color: {BORDER_GLOW};
            background-color: {SURFACE2};
        }}
    """


def input_style(font_size=13, radius=10):
    return f"""
        QLineEdit {{
            background-color: {SURFACE2};
            color: {TEXT_PRI};
            border: 1px solid {BORDER};
            border-radius: {radius}px;
            padding: 10px 14px;
            font-size: {font_size}px;
        }}
        QLineEdit:focus {{
            border: 1px solid {ACCENT1};
        }}
        QLineEdit::placeholder {{
            color: {TEXT_HINT};
        }}
    """


def list_style(font_size=13):
    return f"""
        QListWidget {{
            background-color: {SURFACE2};
            color: {TEXT_PRI};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 6px;
            font-size: {font_size}px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 10px 14px;
            border-radius: 8px;
            margin: 2px 0;
        }}
        QListWidget::item:selected {{
            background-color: {ACCENT_DIM};
            color: #fff;
        }}
        QListWidget::item:hover:!selected {{
            background-color: {SURFACE};
        }}
    """


def dialog_style():
    return f"""
        QDialog {{
            background-color: {SURFACE};
        }}
        QWidget {{
            background-color: {SURFACE};
            color: {TEXT_PRI};
        }}
    """


def progress_bar_style():
    return f"""
        QProgressBar {{
            background-color: {SURFACE2};
            border: 1px solid {BORDER};
            border-radius: 8px;
            height: 16px;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT1}, stop:1 {ACCENT2}
            );
            border-radius: 8px;
        }}
    """