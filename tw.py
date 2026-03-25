# tw.py

import os, json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from paths import BACKEND_FILE

DAYS            = ["Mon","Tue","Wed","Thu","Fri","Sat"]
PERIODS_PER_DAY = 8
DOWNLOADS       = os.path.join(os.path.expanduser("~"), "Downloads")

# -------------------------------------------------------
# These teachers handle practical/special blocks but their
# names don't appear in the class PDF cells — we credit them
# here so they show up in the teacher-wise timetable.
# backend_details.json already tracks this correctly, so
# we just read directly from it.
# -------------------------------------------------------

PHY_CHEM_TEACHERS = {
    "11A": ["RAJANI", "SAJIMON"],
    "12B": ["RAJANI", "SAJIMON"],
    "11B": ["LIJI MATHEW", "POOJA SIHAG"],
    "12A": ["LIJI MATHEW", "POOJA SIHAG"],
}
CS_PRACTICAL_TEACHER  = "SOJU"
BIO_PRACTICAL_TEACHER = "BINDU C"
MATHS_BUSY_TEACHERS   = ["JAYA", "KIRAN", "SOJU"]
MATHS_LEAD_TEACHER    = "JAYA"


# -------------------------------------------------------
# SANITIZE
# -------------------------------------------------------

def sanitize(text):
    if not text:
        return ""
    text = str(text)
    result = []
    for ch in text:
        code = ord(ch)
        if 32 <= code <= 126:
            result.append(ch)
        elif code in (0x2014, 0x2013): result.append("-")
        elif code in (0x2018, 0x2019): result.append("'")
        elif code in (0x201C, 0x201D): result.append('"')
        elif code == 0x2026:           result.append("...")
        elif code == 0x00A0:           result.append(" ")
    return "".join(result).strip()


# -------------------------------------------------------
# LOAD TEACHER GRIDS FROM backend_details.json
#
# backend_details.json structure (written by get.py):
# {
#   "RAJANI": {
#       "subject": "PHYSICS",
#       "grid": [[cls_or_null * 8] * 6]   (6 days × 8 periods)
#   },
#   ...
# }
#
# get.py already correctly populates this grid for:
#   - Regular periods (teacher name in cell)
#   - PHY/CHEM PRACTICAL (via sync_practical_availability)
#   - CS PRACTICAL (SOJU)
#   - BIO PRACTICAL (BINDU C)
#   - MATHS blocks (JAYA as lead, KIRAN+SOJU as paired)
#   - MPT, CCA (placed by rules.py, synced)
# So we just read it directly — no re-parsing needed.
# -------------------------------------------------------

def load_teacher_grids():
    if not os.path.exists(BACKEND_FILE):
        return None, f"backend_details.json not found!\nExpected: {BACKEND_FILE}\nGenerate the timetable first."

    try:
        with open(BACKEND_FILE) as f:
            data = json.load(f)
    except Exception as e:
        return None, f"Error reading backend_details.json: {e}"

    # Validate structure
    grids = {}
    for teacher, info in data.items():
        if not teacher or teacher.strip() in {"—", "-", ""}:
            continue
        subject = sanitize(info.get("subject", ""))
        grid    = info.get("grid", [])

        # Ensure grid is exactly 6 days × 8 periods
        normalized = []
        for day_idx in range(len(DAYS)):
            if day_idx < len(grid):
                row = grid[day_idx]
                # Pad or trim to PERIODS_PER_DAY
                row = list(row) + [None] * PERIODS_PER_DAY
                normalized.append(row[:PERIODS_PER_DAY])
            else:
                normalized.append([None] * PERIODS_PER_DAY)

        grids[teacher] = {
            "subject": subject,
            "grid":    normalized,
        }

    return grids, None


# -------------------------------------------------------
# GENERATE TEACHER-WISE PDF
# Reads backend_details.json → writes teacherwise PDF.
# Every teacher's grid already includes practicals, maths
# blocks, MPT, CCA — all in the correct day+period slots.
# -------------------------------------------------------

def generate_teacherwise_pdf():

    grids, err = load_teacher_grids()
    if err:
        return err

    if not grids:
        return "No teacher data found in backend_details.json."

    sorted_teachers = sorted(grids.keys())

    pdf_path   = os.path.join(DOWNLOADS, "teacherwise_timetable.pdf")
    styles     = getSampleStyleSheet()
    cell_style = ParagraphStyle("CellStyle", fontSize=8, alignment=1, leading=10)
    doc        = SimpleDocTemplate(pdf_path, pagesize=A4)
    content    = []
    col_widths = [2*cm] + [2.5*cm] * PERIODS_PER_DAY

    for teacher in sorted_teachers:
        info    = grids[teacher]
        subject = info["subject"] or "—"
        grid    = info["grid"]

        content.append(
            Paragraph(sanitize(f"Teacher: {teacher} ({subject})"), styles["Title"])
        )
        content.append(Spacer(1, 12))

        header     = ["Day"] + [f"P{p+1}" for p in range(PERIODS_PER_DAY)]
        table_data = [header]

        for day_idx, day_name in enumerate(DAYS):
            row = [day_name]
            for period in range(PERIODS_PER_DAY):
                cls = grid[day_idx][period]
                row.append(sanitize(cls) if cls else "")
            table_data.append(row)

        tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1,  0), colors.lightgrey),
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ]))

        content.append(tbl)
        content.append(PageBreak())

    try:
        doc.build(content)
    except Exception as e:
        return f"Error generating PDF: {e}"

    return (
        f"Teacher-wise PDF generated successfully!\n"
        f"{pdf_path}\n"
        f"({len(sorted_teachers)} teachers)"
    )