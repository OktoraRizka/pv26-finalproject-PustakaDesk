"""
PustakaDesk — ui_laporan.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QFileDialog, QMessageBox,
    QTabWidget, QHeaderView
)

from PySide6.QtCore import Qt
from datetime import datetime

from utils.export import export_csv, export_pdf


class LaporanWidget(QWidget):

    def __init__(self, db):
        super().__init__()

        self.db = db

        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("📊 Laporan")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        root.addWidget(title)

        self.tabs = QTabWidget()

        self.tab_peminjaman = QWidget()
        self.tab_buku = QWidget()

        self.tabs.addTab(
            self.tab_peminjaman,
            "Laporan Peminjaman"
        )

        self.tabs.addTab(
            self.tab_buku,
            "Laporan Katalog Buku"
        )

        root.addWidget(self.tabs)

        self._build_tab_peminjaman()
        self._build_tab_buku()

    def _build_tab_peminjaman(self):

        layout = QVBoxLayout(self.tab_peminjaman)

        top = QHBoxLayout()

        self.combo_status = QComboBox()

        self.combo_status.addItems([
            "Semua",
            "Dipinjam",
            "Terlambat",
            "Dikembalikan"
        ])

        self.combo_status.currentTextChanged.connect(
            self.load_peminjaman
        )

        btn_csv = QPushButton("Ekspor CSV")
        btn_pdf = QPushButton("Ekspor PDF")

        btn_csv.clicked.connect(
            self.export_peminjaman_csv
        )

        btn_pdf.clicked.connect(
            self.export_peminjaman_pdf
        )

        top.addWidget(QLabel("Filter Status:"))
        top.addWidget(self.combo_status)

        top.addStretch()

        top.addWidget(btn_csv)
        top.addWidget(btn_pdf)

        self.table_peminjaman = QTableWidget()

        self.table_peminjaman.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addLayout(top)
        layout.addWidget(self.table_peminjaman)

        self.load_peminjaman()

    def load_peminjaman(self):

        status = self.combo_status.currentText()

        rows = self.db.get_peminjaman_export(status)

        headers = [
            "ID",
            "Judul",
            "Penulis",
            "Nama",
            "Username",
            "Tgl Pinjam",
            "Jatuh Tempo",
            "Tgl Kembali",
            "Status",
            "Denda"
        ]

        self.table_peminjaman.setColumnCount(
            len(headers)
        )

        self.table_peminjaman.setHorizontalHeaderLabels(
            headers
        )

        self.table_peminjaman.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):

                self.table_peminjaman.setItem(
                    i,
                    j,
                    QTableWidgetItem(str(value))
                )

    def export_peminjaman_csv(self):

        status = self.combo_status.currentText()

        rows = self.db.get_peminjaman_export(status)

        headers = [
            "ID",
            "Judul",
            "Penulis",
            "Nama",
            "Username",
            "Tanggal Pinjam",
            "Tanggal Kembali",
            "Tanggal Aktual",
            "Status",
            "Denda"
        ]

        default_name = (
            f"laporan_peminjaman_"
            f"{datetime.now().strftime('%Y%m%d')}.csv"
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan CSV",
            default_name,
            "CSV Files (*.csv)"
        )

        if not filepath:
            return

        export_csv(
            rows,
            filepath,
            headers
        )

        QMessageBox.information(
            self,
            "Berhasil",
            "Laporan CSV berhasil disimpan."
        )

    def export_peminjaman_pdf(self):

        status = self.combo_status.currentText()

        rows = self.db.get_peminjaman_export(status)

        headers = [
            "ID",
            "Judul",
            "Penulis",
            "Nama",
            "Username",
            "Tgl Pinjam",
            "Jatuh Tempo",
            "Tgl Kembali",
            "Status",
            "Denda"
        ]

        default_name = (
            f"laporan_peminjaman_"
            f"{datetime.now().strftime('%Y%m%d')}.pdf"
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan PDF",
            default_name,
            "PDF Files (*.pdf)"
        )

        if not filepath:
            return

        export_pdf(
            rows,
            filepath,
            "Laporan Peminjaman",
            headers,
            f"Filter Status: {status}"
        )

        QMessageBox.information(
            self,
            "Berhasil",
            "Laporan PDF berhasil disimpan."
        )

    def _build_tab_buku(self):

        layout = QVBoxLayout(self.tab_buku)

        top = QHBoxLayout()

        btn_csv = QPushButton("Ekspor CSV")
        btn_pdf = QPushButton("Ekspor PDF")

        btn_csv.clicked.connect(
            self.export_buku_csv
        )

        btn_pdf.clicked.connect(
            self.export_buku_pdf
        )

        top.addStretch()

        top.addWidget(btn_csv)
        top.addWidget(btn_pdf)

        self.table_buku = QTableWidget()

        self.table_buku.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addLayout(top)
        layout.addWidget(self.table_buku)

        self.load_buku()

    def load_buku(self):

        rows = self.db.get_books_export()

        headers = [
            "ID",
            "Judul",
            "Penulis",
            "Penerbit",
            "Tahun",
            "Kategori",
            "Stok",
            "Total"
        ]

        self.table_buku.setColumnCount(
            len(headers)
        )

        self.table_buku.setHorizontalHeaderLabels(
            headers
        )

        self.table_buku.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):

                self.table_buku.setItem(
                    i,
                    j,
                    QTableWidgetItem(str(value))
                )

    def export_buku_csv(self):

        rows = self.db.get_books_export()

        headers = [
            "ID",
            "Judul",
            "Penulis",
            "Penerbit",
            "Tahun",
            "Kategori",
            "Stok",
            "Total Stok"
        ]

        default_name = (
            f"laporan_katalog_"
            f"{datetime.now().strftime('%Y%m%d')}.csv"
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan CSV",
            default_name,
            "CSV Files (*.csv)"
        )

        if not filepath:
            return

        export_csv(
            rows,
            filepath,
            headers
        )

        QMessageBox.information(
            self,
            "Berhasil",
            "Laporan CSV berhasil disimpan."
        )

    def export_buku_pdf(self):

        rows = self.db.get_books_export()

        headers = [
            "ID",
            "Judul",
            "Penulis",
            "Penerbit",
            "Tahun",
            "Kategori",
            "Stok",
            "Total"
        ]

        default_name = (
            f"laporan_katalog_"
            f"{datetime.now().strftime('%Y%m%d')}.pdf"
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan PDF",
            default_name,
            "PDF Files (*.pdf)"
        )

        if not filepath:
            return

        export_pdf(
            rows,
            filepath,
            "Laporan Katalog Buku",
            headers
        )

        QMessageBox.information(
            self,
            "Berhasil",
            "Laporan PDF berhasil disimpan."
        )