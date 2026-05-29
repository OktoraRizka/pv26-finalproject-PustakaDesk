"""
PustakaDesk — main.py
Entry point aplikasi.
Dibuat oleh: [Nama Person 1 - NIM]
"""
import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from database.db_buku import DatabaseBuku


def load_stylesheet(app: QApplication, dark_mode: bool = False):
    style_dir = os.path.join(os.path.dirname(__file__), "style")
    filename  = "style_dark.qss" if dark_mode else "style.qss"
    path      = os.path.join(style_dir, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"[WARN] Stylesheet tidak ditemukan: {path}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PustakaDesk")
    app.setOrganizationName("PV26")

    # Init database
    db = DatabaseBuku()
    db.initialize()
    db.update_status_terlambat()

    # Load stylesheet (terang default)
    load_stylesheet(app, dark_mode=False)

    # Import MainWindow (dibuat oleh Person 2 / 3)
    # ─── UNCOMMENT setelah ui_login.py dan ui_main.py selesai ───
    from ui.ui_login import LoginWindow
    win = LoginWindow(db, app, load_stylesheet)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
