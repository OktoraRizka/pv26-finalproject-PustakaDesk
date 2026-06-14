"""
PustakaDesk — ui_dashboard.py
FINAL: Menampilkan statistik riil & aktivitas terbaru dari Database
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QTableWidget, QHeaderView)
from PySide6.QtCore import Qt

# Import DashboardController dari package logic
from logic.logic import DashboardController
from ui.table_helpers import apply_clean_table_focus

class DashboardWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setObjectName("page")
        self._build_ui()
        
        # Inisialisasi Controller
        self.controller = DashboardController(self)
        
        # Ambil data pertama kali saat halaman dimuat melalui controller
        self.controller.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 26)
        root.setSpacing(18)

        # --- HEADER HALAMAN ---
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
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("subtitle_label")
        self.subtitle.hide()
        text.addWidget(title)

        # Tombol Refresh manual dihubungkan ke controller lewat lambda
        self.btn_refresh = QPushButton("🔄 Refresh Data")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px 14px; 
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.btn_refresh.clicked.connect(lambda: self.controller.refresh())

        header_layout.addWidget(icon)
        header_layout.addLayout(text, 1)
        header_layout.addWidget(self.btn_refresh, 0, Qt.AlignVCenter)
        root.addWidget(header)

        # --- AREA STAT CARD (4 Kolom Horizontal) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_total_buku = self._create_stat_card("📚 Total Buku", "0", "#E3F2FD", "#1E88E5")
        self.card_total_anggota = self._create_stat_card("👥 Total Anggota", "0", "#E8F5E9", "#43A047")
        self.card_dipinjam = self._create_stat_card("📋 Sedang Dipinjam", "0", "#FFF3E0", "#FB8C00")
        self.card_terlambat = self._create_stat_card("⚠️ Terlambat", "0", "#FFEBEE", "#E53935")

        cards_layout.addWidget(self.card_total_buku)
        cards_layout.addWidget(self.card_total_anggota)
        cards_layout.addWidget(self.card_dipinjam)
        cards_layout.addWidget(self.card_terlambat)
        root.addLayout(cards_layout)

        # --- AREA UTAMA / BODY (Aktivitas Terbaru) ---
        body = QFrame()
        body.setObjectName("module_card")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 24, 26, 24)
        body_layout.setSpacing(12)

        module_title = QLabel("⏱️ Aktivitas Peminjaman Terbaru")
        module_title.setObjectName("module_title")
        module_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        body_layout.addWidget(module_title)

        # Tabel Aktivitas Log
        self.table_aktivitas = QTableWidget()
        self.table_aktivitas.setColumnCount(4)
        self.table_aktivitas.setHorizontalHeaderLabels(["Judul Buku", "Nama Peminjam", "Tanggal Pinjam", "Status"])
        self.table_aktivitas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_aktivitas.setSelectionMode(QTableWidget.NoSelection)
        apply_clean_table_focus(self.table_aktivitas)
        
        header_table = self.table_aktivitas.horizontalHeader()
        header_table.setSectionResizeMode(0, QHeaderView.Stretch)
        header_table.setSectionResizeMode(1, QHeaderView.Stretch)
        header_table.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_table.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        body_layout.addWidget(self.table_aktivitas)
        root.addWidget(body, 1)

    def _create_stat_card(self, title, val, bg_color, text_color):
        """Helper untuk membuat stat card yang bersih tanpa border pada teks."""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                border-left: 4px solid {text_color};
                border-radius: 4px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {text_color}; font-weight: 800; font-size: 13px; border: none; background: transparent;")

        lbl_val = QLabel(val)
        lbl_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_val.setStyleSheet(f"color: #111827; font-size: 28px; font-weight: 900; border: none; background: transparent;")

        layout.addWidget(lbl_title)
        layout.addStretch(1)
        layout.addWidget(lbl_val)

        card.setProperty("value_label", lbl_val)
        return card

    def update_card_value(self, card_widget, text_value):
        """Helper visual untuk mengganti teks angka pada stat card."""
        label = card_widget.property("value_label")
        if label:
            label.setText(str(text_value))