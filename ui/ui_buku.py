"""
PustakaDesk — ui_buku.py

Halaman katalog buku untuk admin.
Admin dapat melihat daftar buku, menambah, mengedit, dan menghapus data buku. 
Terdapat fitur pencarian, filter kategori, dan pengurutan untuk memudahkan manajemen koleksi buku.
"""

import os
import re
import shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QHeaderView,
    QAbstractItemView, QDialog, QFormLayout, QSpinBox, QTextEdit,
    QDialogButtonBox, QMessageBox, QFrame, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from logic.logic import BukuController
from ui.table_helpers import apply_clean_table_focus


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COVER_DIR = os.path.join(PROJECT_ROOT, "assets", "covers")


def _absolute_path(path_value: str) -> str:
    """Ubah path relatif project menjadi absolute path yang bisa dibaca QPixmap."""
    if not path_value:
        return ""
    if os.path.isabs(path_value):
        return path_value
    return os.path.join(PROJECT_ROOT, path_value)


def _safe_filename(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip().lower())
    return text.strip("_") or "cover_buku"


class BukuWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setObjectName("page")

        self.init_ui()
        self.controller = BukuController(self)
        self.controller.load_kategori_filter()
        self.controller.load_data()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(12)

        title_block = QVBoxLayout()
        title_block.setSpacing(3)
        title = QLabel("Katalog Buku")
        title.setObjectName("page_title")
        title_block.addWidget(title)

        self.btn_tambah = QPushButton("Tambah Buku")
        self.btn_tambah.setObjectName("btn_primary")
        self.btn_tambah.setCursor(Qt.PointingHandCursor)
        self.btn_tambah.clicked.connect(lambda: self.controller.tambah_buku_aksi(BukuFormDialog))

        header_layout.addLayout(title_block, 1)
        header_layout.addWidget(self.btn_tambah, 0, Qt.AlignVCenter)
        self.main_layout.addWidget(header)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(14, 12, 14, 12)
        toolbar_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul atau penulis...")
        self.search_input.textChanged.connect(lambda: self.controller.load_data())

        self.filter_kategori = QComboBox()
        self.filter_kategori.addItem("Semua Kategori", "All")
        self.filter_kategori.currentIndexChanged.connect(lambda: self.controller.load_data())

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Judul A-Z", "judul_asc")
        self.sort_combo.addItem("Judul Z-A", "judul_desc")
        self.sort_combo.addItem("Tahun Terbaru", "tahun_desc")
        self.sort_combo.addItem("Stok Terkecil", "stok_asc")
        self.sort_combo.currentIndexChanged.connect(lambda: self.controller.load_data())

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setObjectName("btn_secondary")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.clicked.connect(lambda: self.controller.handle_edit(BukuFormDialog))

        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_danger")
        self.btn_hapus.setCursor(Qt.PointingHandCursor)
        self.btn_hapus.clicked.connect(lambda: self.controller.handle_hapus())

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("btn_outline")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(lambda: self.controller.load_data())

        toolbar_layout.addWidget(QLabel("Cari"))
        toolbar_layout.addWidget(self.search_input, 2)
        toolbar_layout.addWidget(QLabel("Kategori"))
        toolbar_layout.addWidget(self.filter_kategori, 1)
        toolbar_layout.addWidget(QLabel("Urutkan"))
        toolbar_layout.addWidget(self.sort_combo, 1)
        toolbar_layout.addSpacing(8)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_hapus)
        toolbar_layout.addWidget(self.btn_refresh)
        self.main_layout.addWidget(toolbar)

        self.table = QTableWidget()
        self.table.setObjectName("data_table")
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Cover", "Judul", "Penulis", "Penerbit", "Tahun", "Kategori", "Tersedia", "Total"
        ])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        apply_clean_table_focus(self.table)
        self.table.cellDoubleClicked.connect(lambda *_: self.controller.handle_edit(BukuFormDialog))
        self.table.setColumnWidth(0, 72)
        self.main_layout.addWidget(self.table, 1)

        hint = QLabel("Tip: klik dua kali pada baris buku untuk membuka dialog edit.")
        hint.setObjectName("hint_label")
        self.main_layout.addWidget(hint)


class BukuFormDialog(QDialog):
    def __init__(self, parent=None, kategori_list=None, book_data=None):
        super().__init__(parent)
        self.book_data = dict(book_data) if book_data else None
        self._image_path = self.book_data.get("image_path", "") if self.book_data else ""
        self._pending_image_source = ""

        self.setWindowTitle("Edit Buku" if self.book_data else "Tambah Buku Baru")
        self.setMinimumWidth(700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        title = QLabel("Edit Data Buku" if self.book_data else "Tambah Data Buku")
        title.setObjectName("dialog_title")
        subtitle = QLabel("Isi data buku dengan rapi. Sampul dan deskripsi akan tampil pada detail buku anggota.")
        subtitle.setObjectName("dialog_subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        content = QHBoxLayout()
        content.setSpacing(18)

        cover_panel = QFrame()
        cover_panel.setObjectName("cover_panel")
        cover_layout = QVBoxLayout(cover_panel)
        cover_layout.setContentsMargins(14, 14, 14, 14)
        cover_layout.setSpacing(10)

        self.cover_preview = QLabel("Tidak ada\ngambar")
        self.cover_preview.setObjectName("cover_preview")
        self.cover_preview.setAlignment(Qt.AlignCenter)
        self.cover_preview.setFixedSize(128, 176)

        self.btn_choose_image = QPushButton("Pilih Gambar")
        self.btn_choose_image.setObjectName("btn_secondary")
        self.btn_choose_image.clicked.connect(self.choose_image)

        self.btn_clear_image = QPushButton("Hapus Gambar")
        self.btn_clear_image.setObjectName("btn_outline")
        self.btn_clear_image.clicked.connect(self.clear_image)

        cover_layout.addWidget(self.cover_preview, 0, Qt.AlignCenter)
        cover_layout.addWidget(self.btn_choose_image)
        cover_layout.addWidget(self.btn_clear_image)
        cover_layout.addStretch()

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)

        self.input_judul = QLineEdit()
        self.input_judul.setPlaceholderText("Contoh: Clean Code")
        self.input_penulis = QLineEdit()
        self.input_penulis.setPlaceholderText("Nama penulis")
        self.input_penerbit = QLineEdit()
        self.input_penerbit.setPlaceholderText("Nama penerbit")

        self.input_tahun = QSpinBox()
        self.input_tahun.setRange(1000, datetime.now().year)
        self.input_tahun.setValue(datetime.now().year)

        self.input_kategori = QComboBox()
        kategori_list = kategori_list or ["Umum", "Novel", "Sains", "Pemrograman", "Sejarah"]
        self.input_kategori.addItems(list(dict.fromkeys([str(k) for k in kategori_list if str(k).strip()])))
        if self.input_kategori.count() == 0:
            self.input_kategori.addItem("Umum")
        self.input_kategori.setEditable(True)

        self.input_stok = QSpinBox()
        self.input_stok.setRange(1, 9999)
        self.input_stok.setValue(1)

        self.input_deskripsi = QTextEdit()
        self.input_deskripsi.setPlaceholderText("Tulis deskripsi singkat isi buku, manfaat, atau gambaran umum buku...")
        self.input_deskripsi.setMinimumHeight(180)

        form_layout.addRow("Judul Buku *", self.input_judul)
        form_layout.addRow("Penulis *", self.input_penulis)
        form_layout.addRow("Penerbit", self.input_penerbit)
        form_layout.addRow("Tahun Terbit", self.input_tahun)
        form_layout.addRow("Kategori", self.input_kategori)
        form_layout.addRow("Total Stok *", self.input_stok)
        form_layout.addRow("Deskripsi", self.input_deskripsi)

        if self.book_data:
            self.input_judul.setText(str(self.book_data.get("judul", "")))
            self.input_penulis.setText(str(self.book_data.get("penulis", "")))
            self.input_penerbit.setText(str(self.book_data.get("penerbit", "")))
            self.input_tahun.setValue(int(self.book_data.get("tahun_terbit") or datetime.now().year))
            kategori = str(self.book_data.get("kategori", "Umum"))
            if self.input_kategori.findText(kategori) < 0:
                self.input_kategori.addItem(kategori)
            self.input_kategori.setCurrentText(kategori)
            self.input_stok.setValue(int(self.book_data.get("total_stok") or self.book_data.get("stok") or 1))
            self.input_deskripsi.setPlainText(str(self.book_data.get("deskripsi", "") or ""))

        form_panel = QFrame()
        form_panel.setObjectName("dialog_form_panel")
        form_panel_layout = QVBoxLayout(form_panel)
        form_panel_layout.setContentsMargins(14, 14, 14, 14)
        form_panel_layout.setSpacing(12)
        form_panel_layout.addLayout(form_layout)


        content.addWidget(cover_panel)
        content.addWidget(form_panel, 1)
        layout.addLayout(content)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._update_preview()

    def choose_image(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih Gambar Sampul",
            "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if filepath:
            self._pending_image_source = filepath
            self._image_path = filepath
            self._update_preview()

    def clear_image(self):
        self._pending_image_source = ""
        self._image_path = ""
        self._update_preview()

    def _copy_pending_image(self) -> str:
        if not self._pending_image_source:
            return self._image_path if self._image_path and not os.path.isabs(self._image_path) else ""

        os.makedirs(COVER_DIR, exist_ok=True)
        _, ext = os.path.splitext(self._pending_image_source)
        ext = ext.lower() if ext else ".png"
        name = _safe_filename(self.input_judul.text())
        filename = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        dest = os.path.join(COVER_DIR, filename)
        shutil.copy2(self._pending_image_source, dest)
        return os.path.relpath(dest, PROJECT_ROOT).replace(os.sep, "/")

    def _update_preview(self):
        path = _absolute_path(self._image_path)
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.cover_preview.setPixmap(
                    pixmap.scaled(128, 176, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.cover_preview.setText("")
                return

        self.cover_preview.setPixmap(QPixmap())
        self.cover_preview.setText("Tidak ada\ngambar")

    def validate_and_accept(self):
        if not self.input_judul.text().strip() or not self.input_penulis.text().strip():
            QMessageBox.warning(self, "Peringatan", "Judul dan Penulis buku wajib diisi.")
            return
        if self.input_stok.value() < 1:
            QMessageBox.warning(self, "Peringatan", "Total stok minimal 1.")
            return
        self.accept()

    def get_data(self):
        image_path = self._copy_pending_image()
        return {
            "judul": self.input_judul.text().strip(),
            "penulis": self.input_penulis.text().strip(),
            "penerbit": self.input_penerbit.text().strip() or "Tidak Ada",
            "tahun_terbit": self.input_tahun.value(),
            "kategori": self.input_kategori.currentText().strip() or "Umum",
            "stok": self.input_stok.value(),
            "total_stok": self.input_stok.value(),
            "image_path": image_path,
            "deskripsi": self.input_deskripsi.toPlainText().strip()
        }
