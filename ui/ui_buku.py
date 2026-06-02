"""
PustakaDesk — ui_buku.py
BELUM DIBUAT

Isi yang harus dibuat:
- class BukuWidget(QWidget)
  - QTableWidget kolom: Judul, Penulis, Penerbit, Tahun, Kategori, Tersedia, Total x
  - Search bar: cari judul / penulis (QLineEdit, textChanged) x
  - Filter: QComboBox kategori (dari db.get_kategori_list()) x
  - Sort: QComboBox (Judul A-Z, Judul Z-A, Tahun, Stok) x
  - Tombol: Tambah, Edit, Hapus, Refresh x
  - Semua form input via QDialog (dari ui_dialogs.py)
  - Hapus: QMessageBox.question konfirmasi
  - Warnai baris stok = 0 merah muda
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QAbstractItemView, QDialog, 
    QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QComboBox,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from logic.logic import BukuController

class BukuWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db  
        
        # 1. Bangun UI Visual terlebih dahulu
        self.init_ui()
        
        # 2. Inisialisasi Controller Logikanya
        self.controller = BukuController(self)
        
        # 3. Panggil fungsi awal LEWAT controller
        self.controller.load_kategori_filter()
        self.controller.load_data()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        # =========================================================
        # PANEL ATAS: SEARCH, FILTER, SORT
        # =========================================================

        self.top_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari Judul atau Penulis...")
        self.search_input.textChanged.connect(lambda: self.controller.load_data())
        
        self.top_layout.addWidget(QLabel("Cari:"))
        self.top_layout.addWidget(self.search_input, stretch=2)

        self.filter_kategori = QComboBox()
        self.filter_kategori.addItem("Semua Kategori", "All")
        self.filter_kategori.currentIndexChanged.connect(lambda: self.controller.load_data())
        
        self.top_layout.addWidget(QLabel("Kategori:"))
        self.top_layout.addWidget(self.filter_kategori, stretch=1)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Judul A-Z", "judul_asc")
        self.sort_combo.addItem("Judul Z-A", "judul_desc")
        self.sort_combo.addItem("Tahun", "tahun_desc")
        self.sort_combo.addItem("Stok", "stok_asc")
        self.sort_combo.currentIndexChanged.connect(lambda: self.controller.load_data())
        
        self.top_layout.addWidget(QLabel("Urutkan:"))
        self.top_layout.addWidget(self.sort_combo, stretch=1)

        self.main_layout.addLayout(self.top_layout)

        # =========================================================
        # TABEL DATA BUKU
        # =========================================================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Judul", "Penulis", "Penerbit", "Tahun", "Kategori", "Tersedia", "Total"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.main_layout.addWidget(self.table)

        # =========================================================
        # PANEL BAWAH: TOMBOL AKSI
        # =========================================================
        self.btn_layout = QHBoxLayout()
        
        self.btn_tambah = QPushButton("➕ Tambah Buku")
        self.btn_edit = QPushButton("✏️ Edit Buku")
        self.btn_hapus = QPushButton("🗑️ Hapus Buku")
        self.btn_refresh = QPushButton("🔄 Refresh")

        # Mengarahkan pemicu trigger event tombol
        self.btn_tambah.clicked.connect(lambda: self.controller.tambah_buku_aksi())
        self.btn_edit.clicked.connect(lambda: self.controller.handle_edit())
        self.btn_hapus.clicked.connect(lambda: self.controller.handle_hapus())
        self.btn_refresh.clicked.connect(lambda: self.controller.load_data())

        self.btn_layout.addWidget(self.btn_tambah)
        self.btn_layout.addWidget(self.btn_edit)
        self.btn_layout.addWidget(self.btn_hapus)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_refresh)

        self.main_layout.addLayout(self.btn_layout)

class BukuFormDialog(QDialog):
    def __init__(self, parent=None, kategori_list=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Buku Baru")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.input_judul = QLineEdit()
        self.input_penulis = QLineEdit()
        self.input_penerbit = QLineEdit()
        
        self.input_tahun = QSpinBox()
        self.input_tahun.setRange(1000, 2100)
        self.input_tahun.setValue(2026)
        
        self.input_kategori = QComboBox()
        if kategori_list:
            self.input_kategori.addItems(kategori_list)
        else:
            self.input_kategori.addItems(["Umum", "Novel", "Sains", "Pemrograman", "Sejarah"])
        self.input_kategori.setEditable(True)
        
        self.input_stok = QSpinBox()
        self.input_stok.setRange(1, 999)
        self.input_stok.setValue(1)
        
        form_layout.addRow("Judul Buku *:", self.input_judul)
        form_layout.addRow("Penulis/Pengarang *:", self.input_penulis)
        form_layout.addRow("Penerbit:", self.input_penerbit)
        form_layout.addRow("Tahun Terbit:", self.input_tahun)
        form_layout.addRow("Kategori:", self.input_kategori)
        form_layout.addRow("Jumlah Stok *:", self.input_stok)
        
        layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def validate_and_accept(self):
        if not self.input_judul.text().strip() or not self.input_penulis.text().strip():
            QMessageBox.warning(self, "Peringatan", "Judul dan Penulis buku wajib diisi!")
            return
        self.accept()

    def get_data(self):
        return {
            "judul": self.input_judul.text().strip(),
            "penulis": self.input_penulis.text().strip(),
            "penerbit": self.input_penerbit.text().strip() or "Tidak Ada",
            "tahun_terbit": self.input_tahun.value(),
            "kategori": self.input_kategori.currentText().strip() or "Umum",
            "stok": self.input_stok.value()
        }

# raise NotImplementedError("ui_buku.py belum dibuat")
