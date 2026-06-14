"""
PustakaDesk — ui_laporan.py
Halaman laporan peminjaman dan katalog buku.
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QFileDialog, QMessageBox,
    QTabWidget, QHeaderView, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt

from utils.export import export_csv, export_pdf
from ui.table_helpers import apply_clean_table_focus


class LaporanWidget(QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QFrame()
        header.setObjectName("page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        title = QLabel("Laporan")
        title.setObjectName("page_title")
        header_layout.addWidget(title, 1)
        root.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("report_tabs")
        self.tab_peminjaman = QWidget()
        self.tab_buku = QWidget()
        self.tabs.addTab(self.tab_peminjaman, "Laporan Peminjaman")
        self.tabs.addTab(self.tab_buku, "Laporan Katalog Buku")
        root.addWidget(self.tabs, 1)

        self._build_tab_peminjaman()
        self._build_tab_buku()

    def _configure_table(self, table):
        table.setObjectName("data_table")
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        apply_clean_table_focus(table)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)

    def _build_tab_peminjaman(self):
        layout = QVBoxLayout(self.tab_peminjaman)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        top = QHBoxLayout(toolbar)
        top.setContentsMargins(14, 12, 14, 12)
        top.setSpacing(10)

        self.combo_status = QComboBox()
        self.combo_status.addItems([
            "Semua", "Aktif", "Menunggu Persetujuan", "Konfirmasi", "Dipinjam",
            "Terlambat", "Riwayat", "Ditolak", "Dikembalikan"
        ])
        self.combo_status.currentTextChanged.connect(self.load_peminjaman)

        btn_csv = QPushButton("Ekspor CSV")
        btn_csv.setObjectName("btn_outline")
        btn_pdf = QPushButton("Ekspor PDF")
        btn_pdf.setObjectName("btn_primary")
        btn_csv.clicked.connect(self.export_peminjaman_csv)
        btn_pdf.clicked.connect(self.export_peminjaman_pdf)

        top.addWidget(QLabel("Filter Status"))
        top.addWidget(self.combo_status)
        top.addStretch()
        top.addWidget(btn_csv)
        top.addWidget(btn_pdf)
        layout.addWidget(toolbar)

        self.table_peminjaman = QTableWidget()
        self._configure_table(self.table_peminjaman)
        layout.addWidget(self.table_peminjaman, 1)
        self.load_peminjaman()

    def load_peminjaman(self):
        status = self.combo_status.currentText()
        rows = self.db.get_peminjaman_export(status)
        headers = [
            "ID", "Judul", "Penulis", "Nama", "Username",
            "Tgl Pinjam", "Jatuh Tempo", "Tgl Kembali", "Status", "Denda"
        ]
        self.table_peminjaman.setColumnCount(len(headers))
        self.table_peminjaman.setHorizontalHeaderLabels(headers)
        self.table_peminjaman.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignCenter if j in (0, 5, 6, 7, 8, 9) else Qt.AlignLeft))
                self.table_peminjaman.setItem(i, j, item)

    def export_peminjaman_csv(self):
        status = self.combo_status.currentText()
        rows = self.db.get_peminjaman_export(status)
        headers = [
            "ID", "Judul", "Penulis", "Nama", "Username",
            "Tanggal Pinjam", "Tanggal Kembali", "Tanggal Aktual", "Status", "Denda"
        ]
        default_name = f"laporan_peminjaman_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", default_name, "CSV Files (*.csv)")
        if not filepath:
            return
        export_csv(rows, filepath, headers)
        QMessageBox.information(self, "Berhasil", "Laporan CSV berhasil disimpan.")

    def export_peminjaman_pdf(self):
        status = self.combo_status.currentText()
        rows = self.db.get_peminjaman_export(status)
        headers = [
            "ID", "Judul", "Penulis", "Nama", "Username",
            "Tgl Pinjam", "Jatuh Tempo", "Tgl Kembali", "Status", "Denda"
        ]
        default_name = f"laporan_peminjaman_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", default_name, "PDF Files (*.pdf)")
        if not filepath:
            return
        export_pdf(rows, filepath, "Laporan Peminjaman", headers, f"Filter Status: {status}")
        QMessageBox.information(self, "Berhasil", "Laporan PDF berhasil disimpan.")

    def _build_tab_buku(self):
        layout = QVBoxLayout(self.tab_buku)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        top = QHBoxLayout(toolbar)
        top.setContentsMargins(14, 12, 14, 12)
        top.setSpacing(10)

        btn_csv = QPushButton("Ekspor CSV")
        btn_csv.setObjectName("btn_outline")
        btn_pdf = QPushButton("Ekspor PDF")
        btn_pdf.setObjectName("btn_primary")
        btn_csv.clicked.connect(self.export_buku_csv)
        btn_pdf.clicked.connect(self.export_buku_pdf)

        top.addStretch()
        top.addWidget(btn_csv)
        top.addWidget(btn_pdf)
        layout.addWidget(toolbar)

        self.table_buku = QTableWidget()
        self._configure_table(self.table_buku)
        layout.addWidget(self.table_buku, 1)
        self.load_buku()

    def load_buku(self):
        rows = self.db.get_books_export()
        headers = ["ID", "Judul", "Penulis", "Penerbit", "Tahun", "Kategori", "Stok", "Total"]
        self.table_buku.setColumnCount(len(headers))
        self.table_buku.setHorizontalHeaderLabels(headers)
        self.table_buku.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignCenter if j in (0, 4, 6, 7) else Qt.AlignLeft))
                self.table_buku.setItem(i, j, item)

    def export_buku_csv(self):
        rows = self.db.get_books_export()
        headers = ["ID", "Judul", "Penulis", "Penerbit", "Tahun", "Kategori", "Stok", "Total"]
        default_name = f"laporan_buku_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", default_name, "CSV Files (*.csv)")
        if not filepath:
            return
        export_csv(rows, filepath, headers)
        QMessageBox.information(self, "Berhasil", "Laporan CSV buku berhasil disimpan.")

    def export_buku_pdf(self):
        rows = self.db.get_books_export()
        headers = ["ID", "Judul", "Penulis", "Penerbit", "Tahun", "Kategori", "Stok", "Total"]
        default_name = f"laporan_buku_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", default_name, "PDF Files (*.pdf)")
        if not filepath:
            return
        export_pdf(rows, filepath, "Laporan Katalog Buku", headers, "Data katalog buku perpustakaan")
        QMessageBox.information(self, "Berhasil", "Laporan PDF buku berhasil disimpan.")

    def refresh(self):
        self.load_peminjaman()
        self.load_buku()
