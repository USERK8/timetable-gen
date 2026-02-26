# rules.py

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS_PER_DAY = 8


def apply_rules(timetable, msc_data):
    """
    Apply school rules:
    1. MPT on Wednesday first period
    2. CCA on Friday first two periods
    3. CS practicals (3 blocks per class, all 11/12)
    4. Phy/Chem practicals (2 blocks per science class)
    5. Maths synchronization rule
    """

    # ---------------------------------------
    # NORMALIZE CLASS NAMES (CASE SAFE)
    # ---------------------------------------
    actual_classes = list(timetable.keys())
    class_map = {cls.upper(): cls for cls in actual_classes}

    def exists(cls_name):
        return cls_name.upper() in class_map

    def get(cls_name):
        return timetable[class_map[cls_name.upper()]]

    # ---------------------------------------
    # LAB TRACKERS (GLOBAL RESOURCES)
    # ---------------------------------------
    cs_lab = [[None for _ in range(PERIODS_PER_DAY)] for _ in DAYS]
    phychem_lab = [[None for _ in range(PERIODS_PER_DAY)] for _ in DAYS]

    # ---------------------------------------
    # WEEKLY TRACKERS
    # ---------------------------------------
    cs_blocks = {cls: 0 for cls in actual_classes}
    phychem_blocks = {cls: 0 for cls in actual_classes}
    practical_days = {cls: set() for cls in actual_classes}

    # ---------------------------------------
    # RULE 1 & 2: MPT and CCA (ALL CLASSES)
    # ---------------------------------------
    for cls in actual_classes:
        table = timetable[cls]

        # Wednesday first period
        table[2][0] = {"subject": "MPT", "teacher": "—"}

        # Friday first two periods
        table[4][0] = {"subject": "CCA", "teacher": "—"}
        table[4][1] = {"subject": "CCA", "teacher": "—"}

    # ---------------------------------------
    # PRACTICAL PLACEMENT ENGINE
    # ---------------------------------------
    def can_place_block(cls, day, period, lab):
        table = timetable[cls]

        if period >= PERIODS_PER_DAY - 1:
            return False

        # Must be empty
        if table[day][period] or table[day][period + 1]:
            return False

        # Must be different day
        if day in practical_days[cls]:
            return False

        # Lab must be free
        lab_tracker = cs_lab if lab == "CS" else phychem_lab
        if lab_tracker[day][period] or lab_tracker[day][period + 1]:
            return False

        return True

    def place_block(cls, day, period, subject, lab):
        timetable[cls][day][period] = {"subject": subject, "teacher": "—"}
        timetable[cls][day][period + 1] = {"subject": subject, "teacher": "—"}

        lab_tracker = cs_lab if lab == "CS" else phychem_lab
        lab_tracker[day][period] = cls
        lab_tracker[day][period + 1] = cls

        practical_days[cls].add(day)

        if lab == "CS":
            cs_blocks[cls] += 1
        else:
            phychem_blocks[cls] += 1

    # ---------------------------------------
    # CS PRACTICALS (3 BLOCKS PER 11/12 CLASS)
    # ---------------------------------------
    for cls in actual_classes:
        if not cls.upper().startswith(("11", "12")):
            continue

        while cs_blocks[cls] < 3:
            placed = False
            for day in range(len(DAYS)):
                for period in range(PERIODS_PER_DAY - 1):
                    if can_place_block(cls, day, period, "CS"):
                        place_block(cls, day, period, "CS Practical", "CS")
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                break  # avoid infinite loop

    # ---------------------------------------
    # PHY/CHEM PRACTICALS (2 BLOCKS SCIENCE ONLY)
    # ---------------------------------------
    for cls in actual_classes:
        if cls.upper() not in ["11A", "11B", "12A", "12B"]:
            continue

        while phychem_blocks[cls] < 2:
            placed = False
            for day in range(len(DAYS)):
                for period in range(PERIODS_PER_DAY - 1):
                    if can_place_block(cls, day, period, "PHY"):
                        place_block(cls, day, period, "Phy/Chem Practical", "PHY")
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                break

    # ---------------------------------------
    # MATHS SYNCHRONIZATION RULE
    # ---------------------------------------
    def enforce_sync(main_cls, dependent_classes):
        if not exists(main_cls):
            return

        main_table = get(main_cls)

        for day in range(len(DAYS)):
            for period in range(PERIODS_PER_DAY):
                cell = main_table[day][period]

                if cell and cell["subject"] == "Maths":
                    for dep in dependent_classes:
                        if exists(dep):
                            dep_table = get(dep)
                            dep_cell = dep_table[day][period]

                            if dep_cell and dep_cell["subject"] not in ["IP", "Hindi", "Maths"]:
                                dep_table[day][period] = None

    # 11th sync
    enforce_sync("11A", ["11B", "11C"])

    # 12th sync
    enforce_sync("12A", ["12B", "12C"])

    return timetable
