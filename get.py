# get.py

import json
import os
import random
import copy

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from rules import apply_rules, sort_classes

MSC_FILE = "msc.json"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS_PER_DAY = 8
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


def generate_timetable_pdfs():

    if not os.path.exists(MSC_FILE):
        return "msc.json not found!"

    with open(MSC_FILE, "r") as f:
        msc_data = json.load(f)

    # Collect all classes (6-12)
    classes = set()
    for t_info in msc_data.values():
        for cls in t_info.get("classes", {}).keys():
            classes.add(cls)

    classes = sort_classes(list(classes))

    best_timetable = None
    best_empty = 999999

    # ---------------------------
    # INITIAL HEAVY-FIRST ALLOCATION
    # ---------------------------
    for attempt in range(40):
        timetable = {cls: [[None]*PERIODS_PER_DAY for _ in range(len(DAYS))] for cls in classes}
        teacher_avail = {teacher: [[True]*PERIODS_PER_DAY for _ in range(len(DAYS))] for teacher in msc_data.keys()}

        # Apply fixed rules from rules.py (MPT, CCA, Practicals)
        timetable = apply_rules(timetable, msc_data)

        # Build teacher tasks
        tasks = []
        teachers_sorted = sorted(
            msc_data.items(),
            key=lambda x: sum(v for c, v in x[1]["classes"].items()),
            reverse=True
        )

        for teacher, info in teachers_sorted:
            subject = info["subject"]
            for cls, count in info["classes"].items():
                for _ in range(count):
                    tasks.append({"teacher": teacher, "class": cls, "subject": subject})

        random.shuffle(tasks)

        # Heavy-first allocation
        for task in tasks:
            cls = task["class"]
            teacher = task["teacher"]
            subject = task["subject"]

            slots = [(d, p) for d in range(len(DAYS)) for p in range(PERIODS_PER_DAY)]
            random.shuffle(slots)

            for day, period in slots:
                if timetable[cls][day][period] is None and teacher_avail[teacher][day][period]:
                    timetable[cls][day][period] = {"subject": subject, "teacher": teacher}
                    teacher_avail[teacher][day][period] = False
                    break

        # Count empty slots
        empty_count = sum(
            1
            for cls in classes
            for d in range(len(DAYS))
            for p in range(PERIODS_PER_DAY)
            if timetable[cls][d][p] is None
        )

        if empty_count < best_empty:
            best_empty = empty_count
            best_timetable = copy.deepcopy(timetable)

        if best_empty == 0:
            break

    timetable = best_timetable

    # ---------------------------
    # REPAIR PASS: fill leftover empty slots
    # ---------------------------

    teacher_avail = {teacher: [[True]*PERIODS_PER_DAY for _ in range(len(DAYS))] for teacher in msc_data.keys()}
    for cls in classes:
        for d in range(len(DAYS)):
            for p in range(PERIODS_PER_DAY):
                cell = timetable[cls][d][p]
                if cell and cell["teacher"] != "—":
                    teacher_avail[cell["teacher"]][d][p] = False

    # Build subjects pool per class
    class_subjects = {}
    for cls in classes:
        subject_pool = []
        for teacher, info in msc_data.items():
            if cls in info["classes"]:
                subject_pool.append({"subject": info["subject"], "teacher": teacher})
        class_subjects[cls] = subject_pool

    # Fill empty slots
    for cls in classes:
        for d in range(len(DAYS)):
            for p in range(PERIODS_PER_DAY):
                if timetable[cls][d][p] is None:
                    possible_subjects = class_subjects[cls][:]
                    random.shuffle(possible_subjects)
                    placed = False
                    for sub in possible_subjects:
                        subject = sub["subject"]
                        teacher = sub["teacher"]

                        if teacher == "—":
                            continue

                        # Max 2 same-sub per day for classes 6-10
                        if cls[:2] in ("6", "7", "8", "9", "10"):
                            count_today = sum(
                                1 for pp in range(PERIODS_PER_DAY)
                                if timetable[cls][d][pp] and timetable[cls][d][pp]["subject"] == subject
                            )
                            if count_today >= 2:
                                continue

                        if teacher_avail[teacher][d][p]:
                            timetable[cls][d][p] = {"subject": subject, "teacher": teacher}
                            teacher_avail[teacher][d][p] = False
                            placed = True
                            break
                    if not placed:
                        continue  # leave empty if no teacher available

    final_empty = sum(
        1
        for cls in classes
        for d in range(len(DAYS))
        for p in range(PERIODS_PER_DAY)
        if timetable[cls][d][p] is None
    )

    # ---------------------------
    # Generate PDF
    # ---------------------------
    pdf_path = os.path.join(DOWNLOADS, "All_Classes_6_to_12_Timetable.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []

    cell_style = ParagraphStyle("CellStyle", fontSize=8, alignment=1, leading=10)
    col_widths = [2*cm] + [2.5*cm]*PERIODS_PER_DAY

    for cls in classes:
        title = Paragraph(f"Class {cls} Timetable", styles["Title"])
        content.append(title)
        content.append(Spacer(1,12))

        header = ["Day"] + [f"P{p+1}" for p in range(PERIODS_PER_DAY)]
        data = [header]

        for day_index, day_name in enumerate(DAYS):
            row = [day_name]
            for period in range(PERIODS_PER_DAY):
                cell = timetable[cls][day_index][period]
                if cell:
                    p = Paragraph(f"<b>{cell['subject']}</b><br/>{cell['teacher']}", cell_style)
                    row.append(p)
                else:
                    row.append("")
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.black),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE")
        ]))
        content.append(tbl)
        content.append(PageBreak())

    doc.build(content)

    return f"Timetable generated using repair-pass allocation.\nEmpty slots: {final_empty}\nExported to {pdf_path}"
