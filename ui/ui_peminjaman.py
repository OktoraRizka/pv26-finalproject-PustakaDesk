"""
PustakaDesk — ui_peminjaman.py
Halaman manajemen peminjaman: pinjam buku, setujui/tolak pengajuan, konfirmasi pengembalian, dan lihat riwayat.
"""

from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QMessageBox, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ui.ui_dialogs import BorrowDialog, ReturnDialog
from ui.table_helpers import apply_clean_table_focus


class PeminjamanWidget(QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QFrame()
        header.setObjectName("page_header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(4)

        title = QLabel("Manajemen Peminjaman")
        title.setObjectName("page_title")
        header_layout.addWidget(title)
        root.addWidget(header)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        top = QHBoxLayout(toolbar)
        top.setContentsMargins(14, 12, 14, 12)
        top.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari judul buku / nama peminjam...")
        self.search.textChanged.connect(self.load_data)

        self.filter_status = QComboBox()
        self.filter_status.addItems([
            "Aktif",
            "Menunggu Persetujuan",
            "Konfirmasi",
            "Dipinjam",
            "Terlambat",
            "Riwayat",
            "Ditolak",
            "Dikembalikan",
            "Semua",
        ])
        self.filter_status.currentTextChanged.connect(self.load_data)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Terbaru", "Terlama", "Jatuh Tempo"])
        self.sort_combo.currentTextChanged.connect(self.load_data)

        top.addWidget(QLabel("Cari"))
        top.addWidget(self.search, 1)
        top.addWidget(QLabel("Tampilan"))
        top.addWidget(self.filter_status)
        top.addWidget(QLabel("Urutkan"))
        top.addWidget(self.sort_combo)
        root.addWidget(toolbar)

        info = QHBoxLayout()
        self.lbl_total = QLabel("Aktif/Proses: 0")
        self.lbl_total.setStyleSheet("color: #334155; font-weight: 750;")
        self.lbl_pengajuan = QLabel("Pengajuan: 0")
        self.lbl_pengajuan.setStyleSheet("color: #2563EB; font-weight: 750;")
        self.lbl_konfirmasi = QLabel("Pengembalian: 0")
        self.lbl_konfirmasi.setStyleSheet("color: #D97706; font-weight: 750;")
        self.lbl_terlambat = QLabel("Terlambat: 0")
        self.lbl_terlambat.setStyleSheet("color: #DC2626; font-weight: 800;")

        info.addWidget(self.lbl_total)
        info.addSpacing(18)
        info.addWidget(self.lbl_pengajuan)
        info.addSpacing(18)
        info.addWidget(self.lbl_konfirmasi)
        info.addSpacing(18)
        info.addWidget(self.lbl_terlambat)
        info.addStretch()
        root.addLayout(info)

        btns = QHBoxLayout()
        btn_pinjam = QPushButton("Pinjam Buku")
        btn_pinjam.setObjectName("btn_primary")
        btn_setujui = QPushButton("Setujui Pengajuan")
        btn_setujui.setObjectName("btn_success")
        btn_tolak = QPushButton("Tolak Pengajuan")
        btn_tolak.setObjectName("btn_danger")
        btn_kembali = QPushButton("Konfirmasi Pengembalian")
        btn_kembali.setObjectName("btn_warning")
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setObjectName("btn_outline")

        btn_pinjam.clicked.connect(self.pinjam_buku)
        btn_setujui.clicked.connect(self.setujui_pengajuan)
        btn_tolak.clicked.connect(self.tolak_pengajuan)
        btn_kembali.clicked.connect(self.kembalikan_buku)
        btn_refresh.clicked.connect(self.load_data)

        btns.addWidget(btn_pinjam)
        btns.addWidget(btn_setujui)
        btns.addWidget(btn_tolak)
        btns.addWidget(btn_kembali)
        btns.addStretch()
        btns.addWidget(btn_refresh)
        root.addLayout(btns)

        self.table = QTableWidget()
        self.table.setObjectName("data_table")
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Judul", "Penulis", "Peminjam", "Tgl Pinjam", "Jatuh Tempo",
            "Tgl Pengajuan/Kembali", "Status", "Denda"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        apply_clean_table_focus(self.table)
        root.addWidget(self.table, 1)

        self.load_data()

    def _status_color(self, status):
        if status == "Terlambat":
            return QColor("#991B1B"), QColor("#FEE2E2")
        if status == "Konfirmasi":
            return QColor("#92400E"), QColor("#FEF3C7")
        if status == "Menunggu Persetujuan":
            return QColor("#1D4ED8"), QColor("#DBEAFE")
        if status == "Ditolak":
            return QColor("#7F1D1D"), QColor("#FEE2E2")
        if status == "Dikembalikan":
            return QColor("#166534"), QColor("#DCFCE7")
        return QColor("#1F2937"), None

    def _current_sort(self):
        sort = self.sort_combo.currentText()
        sort_col = "tanggal_pinjam"
        sort_order = "DESC"
        if sort == "Terlama":
            sort_order = "ASC"
        elif sort == "Jatuh Tempo":
            sort_col = "tanggal_kembali"
            sort_order = "ASC"
        return sort_col, sort_order

    def _selected_loan_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def load_data(self):
        search = self.search.text()
        status = self.filter_status.currentText()
        sort_col, sort_order = self._current_sort()

        rows = self.db.get_all_peminjaman(search, status, sort_col, sort_order)
        self.table.setRowCount(len(rows))

        total_aktif = 0
        total_pengajuan = 0
        total_konfirmasi = 0
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
                f"Rp {int(row['denda']):,}".replace(",", ".")
            ]

            status_text = row["status"]
            fg, bg = self._status_color(status_text)

            for j, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignCenter if j >= 3 else Qt.AlignLeft))
                if j == 0:
                    item.setData(Qt.UserRole, row["id_peminjaman"])
                if bg is not None:
                    item.setBackground(bg)
                if j == 6:
                    item.setForeground(fg)
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

            if status_text in ("Dipinjam", "Terlambat", "Konfirmasi", "Menunggu Persetujuan"):
                total_aktif += 1
            if status_text == "Menunggu Persetujuan":
                total_pengajuan += 1
            if status_text == "Konfirmasi":
                total_konfirmasi += 1
            if status_text == "Terlambat":
                total_terlambat += 1

        self.lbl_total.setText(f"Aktif/Proses: {total_aktif}")
        self.lbl_pengajuan.setText(f"Pengajuan: {total_pengajuan}")
        self.lbl_konfirmasi.setText(f"Pengembalian: {total_konfirmasi}")
        self.lbl_terlambat.setText(f"Terlambat: {total_terlambat}")

    def pinjam_buku(self):
        dialog = BorrowDialog(self.db, self)
        if dialog.exec():
            self.load_data()

    def setujui_pengajuan(self):
        loan_id = self._selected_loan_id()
        if loan_id is None:
            QMessageBox.warning(self, "Pilih Data", "Pilih pengajuan peminjaman terlebih dahulu.")
            return

        data = self.db.get_peminjaman_by_id(loan_id)
        if not data or data["status"] != "Menunggu Persetujuan":
            QMessageBox.information(self, "Bukan Pengajuan", "Data yang dipilih tidak sedang menunggu persetujuan admin.")
            return

        confirm = QMessageBox.question(
            self,
            "Setujui Pengajuan",
            "Setujui peminjaman berdurasi lebih dari 7 hari ini?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.db.setujui_pengajuan_peminjaman(loan_id)
            QMessageBox.information(self, "Berhasil", "Pengajuan peminjaman berhasil disetujui.")
            self.load_data()
        except Exception as exc:
            QMessageBox.warning(self, "Gagal", f"Pengajuan tidak dapat disetujui.\n\n{exc}")

    def tolak_pengajuan(self):
        loan_id = self._selected_loan_id()
        if loan_id is None:
            QMessageBox.warning(self, "Pilih Data", "Pilih pengajuan peminjaman terlebih dahulu.")
            return

        data = self.db.get_peminjaman_by_id(loan_id)
        if not data or data["status"] != "Menunggu Persetujuan":
            QMessageBox.information(self, "Bukan Pengajuan", "Data yang dipilih tidak sedang menunggu persetujuan admin.")
            return

        confirm = QMessageBox.question(
            self,
            "Tolak Pengajuan",
            "Tolak pengajuan peminjaman ini?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.db.tolak_pengajuan_peminjaman(loan_id)
            QMessageBox.information(self, "Pengajuan Ditolak", "Pengajuan ditolak dan stok buku dikembalikan.")
            self.load_data()
        except Exception as exc:
            QMessageBox.warning(self, "Gagal", f"Pengajuan tidak dapat ditolak.\n\n{exc}")

    def kembalikan_buku(self):
        loan_id = self._selected_loan_id()
        if loan_id is None:
            QMessageBox.warning(self, "Pilih Data", "Pilih data peminjaman terlebih dahulu.")
            return

        data = self.db.get_peminjaman_by_id(loan_id)
        if not data:
            QMessageBox.warning(self, "Data Tidak Ditemukan", "Data peminjaman tidak ditemukan.")
            return

        if data["status"] == "Dikembalikan":
            QMessageBox.information(self, "Info", "Buku sudah masuk riwayat pengembalian.")
            return
        if data["status"] == "Menunggu Persetujuan":
            QMessageBox.information(self, "Menunggu Persetujuan", "Setujui atau tolak pengajuan terlebih dahulu.")
            return
        if data["status"] == "Ditolak":
            QMessageBox.information(self, "Pengajuan Ditolak", "Pengajuan ini tidak menjadi peminjaman aktif.")
            return

        if data["status"] == "Konfirmasi":
            confirm = QMessageBox.question(
                self,
                "Konfirmasi Pengembalian",
                "Anggota sudah mengajukan pengembalian.\n\n"
                "Pastikan buku fisik sudah diterima admin, lalu konfirmasi agar stok buku bertambah dan data masuk riwayat.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                try:
                    denda = self.db.kembalikan_buku(loan_id, date.today().isoformat())
                    QMessageBox.information(
                        self,
                        "Berhasil",
                        f"Pengembalian berhasil dikonfirmasi.\nDenda: Rp {int(denda):,}".replace(",", ".")
                    )
                    self.load_data()
                except Exception as e:
                    QMessageBox.warning(self, "Gagal", f"Konfirmasi pengembalian gagal.\n\n{e}")
            return

        dialog = ReturnDialog(self.db, loan_id, date.today().isoformat(), self)
        if dialog.exec():
            self.load_data()
