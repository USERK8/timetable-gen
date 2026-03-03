import random

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS_PER_DAY = 8

# ---------------------------------------
# CLASS SORTING
# ---------------------------------------
def sort_classes(class_list):
    def sort_key(cls):
        num = ""
        sec = ""
        for ch in cls:
            if ch.isdigit():
                num += ch
            else:
                sec += ch
        try:
            return (int(num), sec)
        except:
            return (999, cls)
    return sorted(class_list, key=sort_key)

# ---------------------------------------
# APPLY SCHOOL RULES
# ---------------------------------------
def apply_rules(timetable, msc_data):
    actual_classes = list(timetable.keys())
    class_map = {cls.upper(): cls for cls in actual_classes}

    def exists(cls_name):
        return cls_name.upper() in class_map

    def get(cls_name):
        return timetable[class_map[cls_name.upper()]]

    # ---------------------------------------
    # LAB TRACKERS
    # ---------------------------------------
    cs_lab = [[None]*PERIODS_PER_DAY for _ in DAYS]
    phychem_lab = [[None]*PERIODS_PER_DAY for _ in DAYS]
    bio_lab = [[None]*PERIODS_PER_DAY for _ in DAYS]

    cs_blocks = {cls:0 for cls in actual_classes}
    phychem_blocks = {cls:0 for cls in actual_classes}
    bio_blocks = {"11B":0,"12B":0}

    practical_days = {cls:set() for cls in actual_classes}
    bio_practical_days = {"11B": set(), "12B": set()}

    # ---------------------------------------
    # RULE 1 & 2: MPT & CCA
    # ---------------------------------------
    for cls in actual_classes:
        table = timetable[cls]
        table[2][0] = {"subject":"MPT","teacher":"—"}          # Wednesday 1st
        table[4][0] = {"subject":"CCA","teacher":"—"}          # Friday 1st
        table[4][1] = {"subject":"CCA","teacher":"—"}          # Friday 2nd

    # ---------------------------------------
    # FIXED SUBJECTS: Maths (only 11A/12A)
    # ---------------------------------------
    RESERVED_TEACHERS = {"Maths":"JAYA","CS":"SOJU","Hindi":"KIRAN"}
    SYNC_CLASSES = [("11A",["11B","11C"]), ("12A",["12B","12C"])]

    # Track reserved periods for teachers
    teacher_reserved = {t: [[False]*PERIODS_PER_DAY for _ in DAYS] for t in RESERVED_TEACHERS.values()}

    # Function to place fixed subject in main class (11A / 12A)
    def place_fixed_subject(cls, subject, total_periods):
        table = timetable[cls]
        teacher = RESERVED_TEACHERS[subject]
        placed = 0
        attempts = 0
        while placed < total_periods and attempts < 500:
            day = random.randint(0,len(DAYS)-1)
            period = random.randint(0,PERIODS_PER_DAY-1)

            # Hard constraint: max 2 per class per day
            count_today = sum(1 for p in range(PERIODS_PER_DAY)
                              if table[day][p] and table[day][p]["subject"]==subject)
            if count_today >= 2:
                attempts += 1
                continue

            # Medium constraint: only 1 block per day
            count_today_all = sum(1 for p in range(PERIODS_PER_DAY)
                                  if table[day][p] and table[day][p]["subject"]==subject)
            if count_today_all >=1:
                attempts += 1
                continue

            # Check teacher availability
            if teacher_reserved[teacher][day][period]:
                attempts += 1
                continue

            # Place the subject
            if table[day][period] is None:
                table[day][period] = {"subject":subject, "teacher":teacher}
                teacher_reserved[teacher][day][period] = True
                placed += 1
            attempts += 1

    # Place Maths for 11A / 12A
    if exists("11A"):
        place_fixed_subject("11A", "Maths", 9)
    if exists("12A"):
        place_fixed_subject("12A", "Maths", 9)

    # ---------------------------------------
    # SYNC BLOCKS FOR B/C CLASSES
    # ---------------------------------------
    for main_cls, other_classes in SYNC_CLASSES:
        if not exists(main_cls): continue
        main_table = get(main_cls)
        for day_idx in range(len(DAYS)):
            for period in range(PERIODS_PER_DAY):
                cell = main_table[day_idx][period]
                if not cell: continue
                sub = cell["subject"]
                if sub == "Maths":
                    combined_subject = "Maths/CS/Hindi"
                    combined_teacher = "JAYA/SOJU/KIRAN"
                    # Place in synced classes
                    for oc in other_classes:
                        if exists(oc):
                            oc_table = get(oc)
                            if oc_table[day_idx][period] is None:
                                oc_table[day_idx][period] = {"subject":combined_subject,
                                                             "teacher":combined_teacher}
                                # Mark teachers reserved
                                for t in RESERVED_TEACHERS.values():
                                    teacher_reserved[t][day_idx][period] = True

    # ---------------------------------------
    # PRACTICALS (CS / PHY-CHEM / BIO)
    # Same as before
    # ---------------------------------------
    def can_place_block(cls,day,period,lab):
        table = timetable[cls]
        if period>=PERIODS_PER_DAY-1: return False
        if table[day][period] or table[day][period+1]: return False
        if day in practical_days[cls]: return False
        lab_tracker = cs_lab if lab=="CS" else phychem_lab
        if lab_tracker[day][period] or lab_tracker[day][period+1]: return False
        return True

    def place_block(cls,day,period,subject,lab):
        timetable[cls][day][period] = {"subject":subject,"teacher":"—"}
        timetable[cls][day][period+1] = {"subject":subject,"teacher":"—"}
        lab_tracker = cs_lab if lab=="CS" else phychem_lab
        lab_tracker[day][period] = cls
        lab_tracker[day][period+1] = cls
        practical_days[cls].add(day)
        if lab=="CS": cs_blocks[cls]+=1
        else: phychem_blocks[cls]+=1

    for cls in actual_classes:
        if not cls.startswith(("11","12")): continue
        while cs_blocks[cls]<3:
            placed=False
            for day in range(len(DAYS)):
                for period in range(PERIODS_PER_DAY-1):
                    if can_place_block(cls,day,period,"CS"):
                        place_block(cls,day,period,"CS Practical","CS")
                        placed=True
                        break
                if placed: break
            if not placed: break

    science_classes = ["11A","11B","12A","12B"]
    for cls in actual_classes:
        if cls not in science_classes: continue
        while phychem_blocks[cls]<2:
            placed=False
            for day in range(len(DAYS)):
                for period in range(PERIODS_PER_DAY-1):
                    if can_place_block(cls,day,period,"PHY"):
                        place_block(cls,day,period,"Phy/Chem Practical","PHY")
                        placed=True
                        break
                if placed: break
            if not placed: break

    def can_place_bio(cls,day,period):
        table = timetable[cls]
        if period>=PERIODS_PER_DAY-1: return False
        if table[day][period] or table[day][period+1]: return False
        if day in bio_practical_days[cls]: return False
        if bio_lab[day][period] or bio_lab[day][period+1]: return False
        return True

    def place_bio(cls,day,period):
        timetable[cls][day][period] = {"subject":"Bio Practical","teacher":"—"}
        timetable[cls][day][period+1] = {"subject":"Bio Practical","teacher":"—"}
        bio_lab[day][period] = cls
        bio_lab[day][period+1] = cls
        bio_practical_days[cls].add(day)
        bio_blocks[cls]+=1

    for cls in ["11B","12B"]:
        while bio_blocks[cls]<4:
            placed=False
            for day in range(len(DAYS)):
                for period in range(PERIODS_PER_DAY-1):
                    if can_place_bio(cls,day,period):
                        place_bio(cls,day,period)
                        placed=True
                        break
                if placed: break
            if not placed: break

    return timetable
