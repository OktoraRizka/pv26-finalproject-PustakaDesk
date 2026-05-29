"""
PustakaDesk — ui_dashboard.py
BELUM DIBUAT

File ini tetap ada agar struktur project tidak berubah, tetapi isi dashboard sengaja
berupa template tugas, bukan dashboard final dengan data/statistik jadi.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class DashboardWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setObjectName("page")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 26)
        root.setSpacing(18)

        header = QFrame()
        header.setObjectName("page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 18)
        header_layout.setSpacing(14)

        icon = QLabel("🏠")
        icon.setObjectName("page_icon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(48, 48)

        text = QVBoxLayout()
        text.setSpacing(3)
        title = QLabel("Dashboard Admin")
        title.setObjectName("page_title")
        subtitle = QLabel("Template halaman dashboard. Statistik dan grafik belum dibuat final.")
        subtitle.setObjectName("subtitle_label")
        subtitle.setWordWrap(True)
        text.addWidget(title)
        text.addWidget(subtitle)

        header_layout.addWidget(icon)
        header_layout.addLayout(text, 1)
        root.addWidget(header)

        body = QFrame()
        body.setObjectName("module_card")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 24, 26, 24)
        body_layout.setSpacing(12)

        module_title = QLabel("🏠  Template Modul Dashboard Admin")
        module_title.setObjectName("module_title")

        note = QLabel(
            "Bagian ini disiapkan untuk Anggota lain. Core navigasi dan style sudah tersedia, "
            "tetapi isi dashboard belum dijadikan fitur final."
        )
        note.setObjectName("module_note")
        note.setWordWrap(True)

        todo = QLabel(
            "Yang perlu dibuat:\n"
            "• Stat card: total buku, total anggota, peminjaman aktif, terlambat.\n"
            "• Ringkasan aktivitas terbaru dari database.\n"
            "• Area grafik sederhana jika diperlukan, misalnya peminjaman per kategori/bulan.\n"
            "• Tombol refresh data.\n"
            "• Semua angka harus diambil dari db.get_dashboard_stats(), bukan data dummy."
        )
        todo.setObjectName("module_todo")
        todo.setWordWrap(True)

        body_layout.addWidget(module_title)
        body_layout.addWidget(note)
        body_layout.addWidget(todo)
        body_layout.addStretch()
        root.addWidget(body, 1)

    def refresh(self):
        pass
