"""
PustakaDesk — main.py
Entry point aplikasi.
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


BUILD_VERSION = "v21"


def main():
    print(f"[PustakaDesk {BUILD_VERSION}] Menjalankan: {os.path.abspath(__file__)}")
    app = QApplication(sys.argv)

    # Pada sebagian kombinasi Windows/PySide6, font sistem dapat dilaporkan
    # tanpa point size valid (-1). Tetapkan fallback hanya bila diperlukan.
    app_font = app.font()
    if app_font.pointSize() <= 0:
        app_font.setPointSize(10)
        app.setFont(app_font)

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
    import ui.ui_member as member_module
    print(f"[PustakaDesk {BUILD_VERSION}] UI anggota: {os.path.abspath(member_module.__file__)}")
    win = LoginWindow(db, app, load_stylesheet)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
