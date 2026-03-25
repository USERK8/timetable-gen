# paths.py
# Central path manager for Timetable-Gen.
# All code files live in APP_DIR  (same folder as this script)
# All user data lives in USER_DIR (app_dir/user-dat/)
# On first run, USER_DIR and its empty JSON files are created automatically.

import os
import json

# ── Directories ────────────────────────────────────────────────────────────────

# APP_DIR = wherever main.py / paths.py actually lives
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
USER_DIR = os.path.join(APP_DIR, "user-dat")

# ── User-data file paths ───────────────────────────────────────────────────────

CLASSES_FILE = os.path.join(USER_DIR, "classes.json")
TEACH_FILE   = os.path.join(USER_DIR, "teach_dat.json")
MSC_FILE     = os.path.join(USER_DIR, "msc.json")

# ── App-level file paths ───────────────────────────────────────────────────────

BACKEND_FILE = os.path.join(APP_DIR, "backend_details.json")
VERSION_FILE = os.path.join(APP_DIR, "version.txt")

# ── First-run setup ────────────────────────────────────────────────────────────

def ensure_user_data():
    """
    Called once at startup (from main.py).
    Creates user-dat/ folder and empty JSON files if they don't exist yet.
    Never touches existing files — safe to call on every launch.
    """
    os.makedirs(USER_DIR, exist_ok=True)

    defaults = {
        CLASSES_FILE: [],
        TEACH_FILE:   [],
        MSC_FILE:     {},
    }

    for path, empty_value in defaults.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(empty_value, f, indent=4)


# ── User-data file paths ───────────────────────────────────────────────────────

CLASSES_FILE = os.path.join(USER_DIR, "classes.json")
TEACH_FILE   = os.path.join(USER_DIR, "teach_dat.json")
MSC_FILE     = os.path.join(USER_DIR, "msc.json")

# ── App-level file paths ───────────────────────────────────────────────────────

BACKEND_FILE = os.path.join(APP_DIR, "backend_details.json")
VERSION_FILE = os.path.join(APP_DIR, "version.txt")

# ── First-run setup ────────────────────────────────────────────────────────────

def ensure_user_data():
    """
    Called once at startup (from main.py).
    Creates user-dat/ folder and empty JSON files if they don't exist yet.
    Never touches existing files — safe to call on every launch.
    """
    os.makedirs(USER_DIR, exist_ok=True)

    defaults = {
        CLASSES_FILE: [],
        TEACH_FILE:   [],
        MSC_FILE:     {},
    }

    for path, empty_value in defaults.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(empty_value, f, indent=4)