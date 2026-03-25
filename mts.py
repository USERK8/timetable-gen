import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QInputDialog, QPushButton, QScrollArea,
    QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import QRect, QRectF

from paths import MSC_FILE, CLASSES_FILE

WEEK_MAX = 48   # 6 days × 8 periods


# -------------------------------------------------------
# DATA HELPERS
# -------------------------------------------------------

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
                data = {}
        except json.JSONDecodeError:
            data = {}
    return data


def save_msc(data):
    with open(MSC_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------------------------------------
# BAR CHART WIDGET
# -------------------------------------------------------

class EngagementChart(QWidget):
    """Custom bar chart — no matplotlib needed."""

    BAR_COLOR      = QColor("#4a9eff")
    BAR_WARN_COLOR = QColor("#f0a500")   # approaching limit  (>= 40)
    BAR_OVER_COLOR = QColor("#e05555")   # over limit         (> 48)
    BG_COLOR       = QColor("#161616")
    GRID_COLOR     = QColor("#2a2a2a")
    TEXT_COLOR      = QColor("#cccccc")
    LIMIT_COLOR    = QColor("#e05555")

    PAD_LEFT   = 60
    PAD_RIGHT  = 30
    PAD_TOP    = 30
    PAD_BOTTOM = 90   # room for rotated teacher names

    def __init__(self, data, parent=None):
        """data: list of (teacher_name, total_periods) sorted desc."""
        super().__init__(parent)
        self.data = data
        self.setMinimumHeight(420)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        if not self.data:
            return

        p   = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W = self.width()
        H = self.height()

        # Background
        p.fillRect(0, 0, W, H, self.BG_COLOR)

        chart_w = W - self.PAD_LEFT - self.PAD_RIGHT
        chart_h = H - self.PAD_TOP  - self.PAD_BOTTOM

        max_val  = max(v for _, v in self.data) if self.data else 1
        y_max    = max(max_val + 4, WEEK_MAX + 4)

        n        = len(self.data)
        bar_w    = max(18, min(54, (chart_w - (n + 1) * 6) // n))
        gap      = (chart_w - n * bar_w) // (n + 1)

        # Grid lines + Y labels
        p.setFont(QFont("Arial", 9))
        step = 8
        grid_steps = range(0, y_max + 1, step)
        for val in grid_steps:
            y = self.PAD_TOP + chart_h - int(val / y_max * chart_h)
            p.setPen(QPen(self.GRID_COLOR, 1))
            p.drawLine(self.PAD_LEFT, y, self.PAD_LEFT + chart_w, y)
            p.setPen(QPen(self.TEXT_COLOR))
            p.drawText(QRect(0, y - 10, self.PAD_LEFT - 6, 20),
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                       str(val))

        # WEEK_MAX limit line
        limit_y = self.PAD_TOP + chart_h - int(WEEK_MAX / y_max * chart_h)
        p.setPen(QPen(self.LIMIT_COLOR, 1, Qt.PenStyle.DashLine))
        p.drawLine(self.PAD_LEFT, limit_y, self.PAD_LEFT + chart_w, limit_y)
        p.setPen(QPen(self.LIMIT_COLOR))
        p.setFont(QFont("Arial", 8))
        p.drawText(self.PAD_LEFT + chart_w - 60, limit_y - 4, f"Max ({WEEK_MAX})")

        # Bars
        for i, (name, val) in enumerate(self.data):
            x    = self.PAD_LEFT + gap + i * (bar_w + gap)
            bh   = int(val / y_max * chart_h)
            y    = self.PAD_TOP + chart_h - bh

            if val > WEEK_MAX:
                color = self.BAR_OVER_COLOR
            elif val >= 40:
                color = self.BAR_WARN_COLOR
            else:
                color = self.BAR_COLOR

            # Bar with slight gradient
            grad = QLinearGradient(x, y, x, y + bh)
            grad.setColorAt(0, color.lighter(120))
            grad.setColorAt(1, color)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(x, y, bar_w, bh), 4, 4)

            # Value label above bar
            p.setPen(QPen(self.TEXT_COLOR))
            p.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            p.drawText(QRect(x, y - 20, bar_w, 18),
                       Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                       str(val))

            # Teacher name — rotated below bar
            p.save()
            p.translate(x + bar_w / 2, self.PAD_TOP + chart_h + 10)
            p.rotate(40)
            p.setFont(QFont("Arial", 8))
            p.setPen(QPen(self.TEXT_COLOR))
            p.drawText(0, 0, name)
            p.restore()

        # Axes
        p.setPen(QPen(QColor("#555555"), 1))
        p.drawLine(self.PAD_LEFT, self.PAD_TOP,
                   self.PAD_LEFT, self.PAD_TOP + chart_h)
        p.drawLine(self.PAD_LEFT, self.PAD_TOP + chart_h,
                   self.PAD_LEFT + chart_w, self.PAD_TOP + chart_h)

        # Y-axis label
        p.save()
        p.translate(14, self.PAD_TOP + chart_h // 2)
        p.rotate(-90)
        p.setFont(QFont("Arial", 10))
        p.setPen(QPen(self.TEXT_COLOR))
        p.drawText(QRect(-80, -10, 160, 20),
                   Qt.AlignmentFlag.AlignCenter, "Periods / week")
        p.restore()

        p.end()


# -------------------------------------------------------
# ENGAGEMENT GRAPH DIALOG
# -------------------------------------------------------

class EngagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Teacher Engagement")
        self.setMinimumSize(820, 560)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("QDialog { background-color: #141414; }")

        root = QVBoxLayout()
        root.setSpacing(16)
        root.setContentsMargins(28, 24, 28, 24)

        # Title
        title = QLabel("Teacher Engagement")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff4ecd;")
        root.addWidget(title)

        subtitle = QLabel("Total periods assigned per teacher this week — sorted by busiest first")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #777777;")
        root.addWidget(subtitle)

        # Legend
        legend_row = QHBoxLayout()
        legend_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legend_row.setSpacing(24)

        for color, label in [
            ("#4a9eff", "Normal"),
            ("#f0a500", "High (≥ 40)"),
            ("#e05555", "Overbooked (> 48)"),
        ]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            legend_row.addWidget(dot)
            legend_row.addWidget(lbl)

        # Limit line legend
        dash = QLabel("- - -")
        dash.setStyleSheet("color: #e05555; font-size: 11px; letter-spacing: 2px;")
        lbl_limit = QLabel(f"Max ({WEEK_MAX} periods)")
        lbl_limit.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        legend_row.addWidget(dash)
        legend_row.addWidget(lbl_limit)

        root.addLayout(legend_row)

        # Chart (inside scroll area in case there are many teachers)
        msc_data = load_msc()
        chart_data = sorted(
            [
                (teacher, sum(info.get("classes", {}).values()))
                for teacher, info in msc_data.items()
                if info.get("classes")
            ],
            key=lambda x: x[1],
            reverse=True
        )

        if chart_data:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea { border: none; background: transparent; }
                QScrollBar:horizontal {
                    height: 10px; background: #1e1e1e; border-radius: 5px;
                }
                QScrollBar::handle:horizontal {
                    background: #3a3a3a; border-radius: 5px; min-width: 30px;
                }
            """)

            min_chart_w = max(820, len(chart_data) * 70)
            self.chart  = EngagementChart(chart_data)
            self.chart.setMinimumWidth(min_chart_w)
            scroll.setWidget(self.chart)
            root.addWidget(scroll)
        else:
            empty = QLabel("No teacher schedule data found.\nAssign periods via Manage Teacher's Schedule first.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #666666; font-size: 13px;")
            root.addWidget(empty)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.setFixedHeight(40)
        btn_close.setFont(QFont("Arial", 11))
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #aaaaaa;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #333333; color: white; }
        """)
        root.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(root)


# -------------------------------------------------------
# MANAGE TEACHER SCHEDULE DIALOG
# -------------------------------------------------------

class ManageTeacherSchedule(QDialog):
    def __init__(self, teacher_name, subject, parent=None):
        super().__init__(parent)

        self.teacher_name = teacher_name
        self.subject      = subject

        self.setWindowTitle("Manage Teacher Schedule")
        self.setMinimumWidth(380)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("QDialog { background-color: #141414; }")

        root = QVBoxLayout()
        root.setSpacing(12)
        root.setContentsMargins(28, 24, 28, 24)

        title = QLabel(f"{teacher_name}'s Schedule")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff4ecd;")
        root.addWidget(title)

        # Period counter label (updates live)
        self.period_label = QLabel()
        self.period_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.period_label.setFont(QFont("Arial", 10))
        root.addWidget(self.period_label)

        # Scrollable checkbox area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: 1px solid #2a2a2a; border-radius: 8px; background: #1a1a1a; }
            QScrollBar:vertical { width: 8px; background: #1a1a1a; }
            QScrollBar::handle:vertical { background: #3a3a3a; border-radius: 4px; }
        """)

        inner = QWidget()
        inner.setStyleSheet("background: #1a1a1a;")
        inner_layout = QVBoxLayout()
        inner_layout.setSpacing(6)
        inner_layout.setContentsMargins(14, 10, 14, 10)

        self.classes   = load_classes()
        self.checkboxes = []
        self.msc_data  = load_msc()
        teacher_classes = self.msc_data.get(self.teacher_name, {}).get("classes", {})

        cb_style = """
            QCheckBox { color: #cccccc; font-size: 12px; padding: 4px; }
            QCheckBox::indicator { width: 16px; height: 16px; border: 2px solid #3a3a3a;
                border-radius: 4px; background: #222222; }
            QCheckBox::indicator:checked { background: #4a9eff; border-color: #4a9eff; }
        """

        for cls in self.classes:
            cb = QCheckBox(cls)
            cb.setStyleSheet(cb_style)
            if cls in teacher_classes:
                cb.setChecked(True)
            cb.stateChanged.connect(self.class_checked)
            inner_layout.addWidget(cb)
            self.checkboxes.append(cb)

        inner.setLayout(inner_layout)
        scroll.setWidget(inner)
        root.addWidget(scroll)

        self.setLayout(root)
        self._update_period_label()

    # Live period counter
    def _total_periods(self):
        data = load_msc()
        return sum(data.get(self.teacher_name, {}).get("classes", {}).values())

    def _update_period_label(self):
        total = self._total_periods()
        if total > WEEK_MAX:
            color = "#e05555"
            note  = f"⚠ Overbooked! ({total} / {WEEK_MAX})"
        elif total >= 40:
            color = "#f0a500"
            note  = f"⚡ High load ({total} / {WEEK_MAX})"
        else:
            color = "#4a9eff"
            note  = f"{total} / {WEEK_MAX} periods assigned"
        self.period_label.setText(note)
        self.period_label.setStyleSheet(f"color: {color}; font-size: 11px;")

    def class_checked(self, state):
        checkbox = self.sender()
        if state == Qt.CheckState.Checked.value:
            periods, ok = QInputDialog.getInt(
                self,
                "Enter Periods",
                f"Number of {self.subject} periods per week for {checkbox.text()}:",
                1, 1, WEEK_MAX
            )
            if ok:
                self.save_data(checkbox.text(), periods)
                self._update_period_label()
            else:
                checkbox.setChecked(False)
        else:
            self.remove_class(checkbox.text())
            self._update_period_label()

    def save_data(self, class_name, periods):
        data = load_msc()
        if self.teacher_name not in data:
            data[self.teacher_name] = {"subject": self.subject, "classes": {}}
        data[self.teacher_name]["classes"][class_name] = periods
        save_msc(data)

    def remove_class(self, class_name):
        data = load_msc()
        if self.teacher_name in data and class_name in data[self.teacher_name]["classes"]:
            del data[self.teacher_name]["classes"][class_name]
            save_msc(data)