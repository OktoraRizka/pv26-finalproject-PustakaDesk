"""
PustakaDesk — ui_peminjaman.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit,
    QComboBox, QMessageBox, QHeaderView
)

from PySide6.QtCore import Qt
from datetime import date

from ui.ui_dialogs import BorrowDialog, ReturnDialog


class PeminjamanWidget(QWidget):

    def __init__(self, db):
        super().__init__()

        self.db = db

        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("📋 Manajemen Peminjaman")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        root.addWidget(title)

        top = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Cari judul buku / nama peminjam..."
        )

        self.search.textChanged.connect(
            self.load_data
        )

        self.filter_status = QComboBox()

        self.filter_status.addItems([
            "Semua",
            "Dipinjam",
            "Terlambat",
            "Dikembalikan"
        ])

        self.filter_status.currentTextChanged.connect(
            self.load_data
        )

        self.sort_combo = QComboBox()

        self.sort_combo.addItems([
            "Terbaru",
            "Terlama",
            "Jatuh Tempo"
        ])

        self.sort_combo.currentTextChanged.connect(
            self.load_data
        )

        top.addWidget(self.search)
        top.addWidget(self.filter_status)
        top.addWidget(self.sort_combo)

        root.addLayout(top)

        info = QHBoxLayout()

        self.lbl_total = QLabel("Dipinjam: 0")
        self.lbl_terlambat = QLabel("Terlambat: 0")

        self.lbl_terlambat.setStyleSheet(
            "color: red; font-weight: bold;"
        )

        info.addWidget(self.lbl_total)
        info.addSpacing(20)
        info.addWidget(self.lbl_terlambat)
        info.addStretch()

        root.addLayout(info)

        btns = QHBoxLayout()

        btn_pinjam = QPushButton("Pinjam Buku")
        btn_kembali = QPushButton("Kembalikan")
        btn_refresh = QPushButton("Refresh")

        btn_pinjam.clicked.connect(
            self.pinjam_buku
        )

        btn_kembali.clicked.connect(
            self.kembalikan_buku
        )

        btn_refresh.clicked.connect(
            self.load_data
        )

        btns.addWidget(btn_pinjam)
        btns.addWidget(btn_kembali)
        btns.addStretch()
        btns.addWidget(btn_refresh)

        root.addLayout(btns)

        self.table = QTableWidget()

        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels([
            "Judul",
            "Penulis",
            "Peminjam",
            "Tgl Pinjam",
            "Tgl Kembali",
            "Tgl Dikembalikan",
            "Status",
            "Denda"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        root.addWidget(self.table)

        self.load_data()

    def load_data(self):

        search = self.search.text()

        status = self.filter_status.currentText()

        sort = self.sort_combo.currentText()

        sort_col = "tanggal_pinjam"
        sort_order = "DESC"

        if sort == "Terlama":
            sort_order = "ASC"

        elif sort == "Jatuh Tempo":
            sort_col = "tanggal_kembali"
            sort_order = "ASC"

        rows = self.db.get_all_peminjaman(
            search,
            status,
            sort_col,
            sort_order
        )

        self.table.setRowCount(len(rows))

        total_dipinjam = 0
        total_terlambat = 0

        for i, row in enumerate(rows):

            values = [
                row["judul"],
                row["penulis"],
                row["nama_lengkap"],
                row["tanggal_pinjam"],
                row["tanggal_kembali"],
                row["tanggal_kembali_aktual"] or "-",
                row["status"],
                str(row["denda"])
            ]

            for j, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                item.setFlags(
                    item.flags() ^ Qt.ItemIsEditable
                )

                if row["status"] == "Terlambat":
                    item.setBackground(
                        Qt.GlobalColor.lightGray
                    )

                self.table.setItem(i, j, item)

            if row["status"] in [
                "Dipinjam",
                "Terlambat"
            ]:
                total_dipinjam += 1

            if row["status"] == "Terlambat":
                total_terlambat += 1

        self.lbl_total.setText(
            f"Dipinjam: {total_dipinjam}"
        )

        self.lbl_terlambat.setText(
            f"Terlambat: {total_terlambat}"
        )

    def pinjam_buku(self):

        dialog = BorrowDialog(self.db)

        if dialog.exec():
            self.load_data()

    def kembalikan_buku(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Pilih Data",
                "Pilih data peminjaman terlebih dahulu."
            )
            return

        search = self.search.text()

        status = self.filter_status.currentText()

        rows = self.db.get_all_peminjaman(
            search,
            status
        )

        data = rows[row]

        if data["status"] == "Dikembalikan":

            QMessageBox.information(
                self,
                "Info",
                "Buku sudah dikembalikan."
            )

            return

        today = date.today().isoformat()

        dialog = ReturnDialog(
            self.db,
            data["id_peminjaman"],
            today
        )

        if dialog.exec():
            self.load_data()