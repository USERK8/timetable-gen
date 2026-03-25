# update.py

import os
import requests
from PyQt6.QtWidgets import QMessageBox
from paths import APP_DIR, VERSION_FILE

# GitHub repo raw URLs
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/USERK8/stt/main/"

# Only code files — user-dat/ JSON files are NEVER touched by updates
FILES_TO_UPDATE = [
    "main.py",
    "mc.py",
    "mt.py",
    "mts.py",
    "s.py",
    "get.py",
    "rules.py",
    "tw.py",
    "dw.py",
    "pet.py",
    "paths.py",
    "update.py",
    "version.txt",
    "about this folder",
]


def fetch_remote_version():
    url = GITHUB_RAW_BASE + "version.txt"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        print("Error fetching remote version:", e)
        return None


def fetch_local_version():
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()


def download_file(file_name):
    url = GITHUB_RAW_BASE + file_name
    dest = os.path.join(APP_DIR, file_name)
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"Failed to download {file_name}: {e}")
        return False


def check_for_update(parent=None):
    remote_version = fetch_remote_version()
    local_version = fetch_local_version()
    if not remote_version:
        return False

    if remote_version > local_version:
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Update Available")
        msg.setText(
            f"A new version ({remote_version}) is available.\nYour version: {local_version}"
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        ret = msg.exec()

        if ret == QMessageBox.StandardButton.Yes:
            success_files = []
            failed_files = []
            for f in FILES_TO_UPDATE:
                if download_file(f):
                    success_files.append(f)
                else:
                    failed_files.append(f)

            if failed_files:
                msg2 = QMessageBox(parent)
                msg2.setIcon(QMessageBox.Icon.Critical)
                msg2.setWindowTitle("Update Failed")
                msg2.setText(
                    f"Some files could not be updated:\n{', '.join(failed_files)}"
                )
                msg2.exec()
            else:
                msg3 = QMessageBox(parent)
                msg3.setIcon(QMessageBox.Icon.Information)
                msg3.setWindowTitle("Update Complete")
                msg3.setText("All files updated successfully!\nPlease restart the app.")
                msg3.exec()
                return True
    return False