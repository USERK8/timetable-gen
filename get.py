# get.py

import json, os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from rules import apply_rules

MSC_FILE = "msc.json"
DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat"]
PERIODS_PER_DAY = 8
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


def generate_timetable_pdfs():

    if not os.path.exists(MSC_FILE):
        return "msc.json not found!"

    with open(MSC_FILE,"r") as f:
        msc_data = json.load(f)

    # -------- Collect Classes --------
    classes = set()
    for t_info in msc_data.values():
        classes.update(t_info.get("classes",{}).keys())

    timetable = {cls: [[None]*PERIODS_PER_DAY for _ in range(len(DAYS))] for cls in classes}
    teacher_avail = {
        teacher: [[True]*PERIODS_PER_DAY for _ in range(len(DAYS))]
        for teacher in msc_data.keys()
    }

    # -------- Pre-Apply Fixed Rules --------
    temp_tt = {cls: [[None]*PERIODS_PER_DAY for _ in range(len(DAYS))] for cls in classes}
    temp_tt = apply_rules(temp_tt, msc_data)

    for cls in classes:
        for d in range(len(DAYS)):
            for p in range(PERIODS_PER_DAY):
                if temp_tt[cls][d][p] is not None:
                    timetable[cls][d][p] = temp_tt[cls][d][p]
                    for teacher in teacher_avail:
                        teacher_avail[teacher][d][p] = False

    # -------- Build Subject Pool --------
    class_subjects = {}

    for cls in classes:
        subject_pool = []
        for teacher, info in msc_data.items():
            subject = info["subject"]
            if cls in info["classes"]:
                count = info["classes"][cls]
                subject_pool.append({
                    "subject": subject,
                    "teacher": teacher,
                    "remaining": count
                })
        class_subjects[cls] = subject_pool

    # -------- Day-wise Balanced Filling --------
    for cls in classes:

        subjects = class_subjects[cls]

        for day in range(len(DAYS)):

            subject_index = 0

            for period in range(PERIODS_PER_DAY):

                # Skip fixed rule slots
                if timetable[cls][day][period] is not None:
                    continue

                attempts = 0

                while attempts < len(subjects):

                    subj_data = subjects[subject_index % len(subjects)]
                    subject = subj_data["subject"]
                    teacher = subj_data["teacher"]

                    if subj_data["remaining"] > 0 and teacher_avail[teacher][day][period]:

                        # Prevent same subject same period consecutive day
                        if day > 0:
                            prev = timetable[cls][day-1][period]
                            if prev and prev["subject"] == subject:
                                subject_index += 1
                                attempts += 1
                                continue

                        # Place subject
                        timetable[cls][day][period] = {
                            "subject": subject,
                            "teacher": teacher
                        }

                        teacher_avail[teacher][day][period] = False
                        subj_data["remaining"] -= 1
                        subject_index += 1
                        break

                    subject_index += 1
                    attempts += 1

    # -------- Export PDF --------
    pdf_path = os.path.join(DOWNLOADS, "All_Classes_Timetable.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []

    cell_style = ParagraphStyle(
        "CellStyle",
        fontSize=8,
        alignment=1,
        leading=10,
    )

    # Days as ROWS, Periods as COLUMNS
    col_widths = [2*cm] + [2.5*cm]*PERIODS_PER_DAY

    for cls, table_data in timetable.items():

        title = Paragraph(f"Class {cls} Timetable", styles["Title"])
        content.append(title)
        content.append(Spacer(1, 12))

        # Header row
        header = ["Day"] + [f"P{p+1}" for p in range(PERIODS_PER_DAY)]
        data = [header]

        for day_index, day_name in enumerate(DAYS):
            row = [day_name]
            for period in range(PERIODS_PER_DAY):
                cell = table_data[day_index][period]
                if cell:
                    p = Paragraph(
                        f"<b>{cell['subject']}</b><br/>{cell['teacher']}",
                        cell_style
                    )
                    row.append(p)
                else:
                    row.append("")
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.black),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))

        content.append(tbl)
        content.append(PageBreak())

    doc.build(content)

    return f"All class timetables exported to {pdf_path}"
