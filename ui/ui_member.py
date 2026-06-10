"""
PustakaDesk — ui_member.py

File ini berisi widget halaman anggota seperti Beranda, Cari Buku,
Pinjaman Saya, Riwayat, dan Profil. Navigasi utama tetap diatur dari ui_main.py.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QScrollArea, QGridLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from datetime import date, timedelta

def _row_to_dict(row):
    try:
        return dict(row)
    except Exception:
        return row if isinstance(row, dict) else {}


def _member_id(user):
    user = _row_to_dict(user)
    return user.get("id_user") or user.get("id")


class MemberHomeWidget(QWidget):
    def __init__(self, db, user: dict, go_to_callback=None):
        super().__init__()

        self.db = db
        self.user = _row_to_dict(user)
        self.go_to = go_to_callback

        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("module_card")

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(12)

        welcome = QLabel(
            f"✨ Selamat Datang, {self.user.get('nama_lengkap', 'Anggota')}"
        )
        welcome.setStyleSheet(
            "font-size:22px; font-weight:bold;"
        )

        subtitle = QLabel(
            "Cari buku, lihat status pinjaman, dan temukan rekomendasi bacaan terbaru."
        )
        subtitle.setWordWrap(True)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Cari judul atau penulis buku..."
        )

        hero_layout.addWidget(welcome)
        hero_layout.addWidget(subtitle)
        hero_layout.addWidget(self.search_input)

        root.addWidget(hero)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        total_active = 0
        total_late = 0
        total_history = 0
        total_books = 0

        if hasattr(self.db, "get_member_stats"):
            stats = self.db.get_member_stats(_member_id(self.user))

            total_active = stats.get("dipinjam", 0)
            total_late = stats.get("terlambat", 0)
            total_history = stats.get("riwayat", 0)
            total_books = stats.get("tersedia", 0)

        cards = [
            ("📖", "Pinjaman Aktif", total_active),
            ("⚠️", "Terlambat", total_late),
            ("🕘", "Riwayat", total_history),
            ("📚", "Buku Tersedia", total_books),
        ]

        for icon, text, value in cards:
            card = QFrame()
            card.setObjectName("module_card")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 18, 18, 18)

            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("font-size:22px;")

            value_label = QLabel(str(value))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet(
                "font-size:20px; font-weight:bold;"
            )

            text_label = QLabel(text)
            text_label.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(icon_label)
            card_layout.addWidget(value_label)
            card_layout.addWidget(text_label)

            stats_layout.addWidget(card)

        root.addLayout(stats_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        catalog_btn = QPushButton("🔎 Cari Buku")
        loans_btn = QPushButton("📖 Pinjaman Saya")

        if self.go_to:
            catalog_btn.clicked.connect(
                lambda: self.go_to("Cari Buku")
            )

            loans_btn.clicked.connect(
                lambda: self.go_to("Pinjaman Saya")
            )

        action_layout.addWidget(catalog_btn)
        action_layout.addWidget(loans_btn)

        root.addLayout(action_layout)

        recommendation_title = QLabel("📚 Buku Terbaru")
        recommendation_title.setStyleSheet(
            "font-size:18px; font-weight:bold;"
        )

        root.addWidget(recommendation_title)

        books_layout = QVBoxLayout()
        books_layout.setSpacing(12)

        books = []

        if hasattr(self.db, "get_all_books"):
            books = [ _row_to_dict(book) for book in self.db.get_all_books()][:5]

        for book in books:
            card = QFrame()
            card.setObjectName("module_card")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 18, 18, 18)

            title = QLabel(
                f"📘 {book.get('judul', '-')}"
            )
            title.setStyleSheet(
                "font-size:16px; font-weight:bold;"
            )

            author = QLabel(
                f"Penulis: {book.get('penulis', '-')}"
            )

            category = QLabel(
                f"Kategori: {book.get('kategori', '-')}"
            )

            stock = QLabel(
                f"Stok: {book.get('stok', 0)}"
            )

            card_layout.addWidget(title)
            card_layout.addWidget(author)
            card_layout.addWidget(category)
            card_layout.addWidget(stock)

            books_layout.addWidget(card)

        root.addLayout(books_layout)
        root.addStretch()

    def refresh(self):
        pass


class MemberCatalogWidget(QWidget):
    def __init__(self, db, user: dict):
        super().__init__()

        self.db = db
        self.user = _row_to_dict(user)

        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("🔎 Cari Buku")
        title.setStyleSheet(
            "font-size:22px; font-weight:bold;"
        )

        subtitle = QLabel(
            "Cari buku dan lakukan peminjaman langsung dari katalog."
        )

        root.addWidget(title)
        root.addWidget(subtitle)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Cari judul atau penulis..."
        )

        self.category_filter = QComboBox()
        self.category_filter.addItem("Semua Kategori")

        if hasattr(self.db, "get_kategori_list"):
            for kategori in self.db.get_kategori_list():
                self.category_filter.addItem(kategori)

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.category_filter)

        root.addLayout(top_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.books_layout = QGridLayout(self.container)
        self.books_layout.setSpacing(16)

        self.scroll.setWidget(self.container)

        root.addWidget(self.scroll)

        self.search_input.textChanged.connect(
            self.load_books
        )

        self.category_filter.currentTextChanged.connect(
            self.load_books
        )

        self.load_books()

    def load_books(self):
        while self.books_layout.count():
            item = self.books_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        books = []

        if hasattr(self.db, "get_all_books"):
            books = [ _row_to_dict(book) for book in self.db.get_all_books()]

        keyword = self.search_input.text().lower()
        kategori = self.category_filter.currentText()

        filtered = []

        for book in books:
            judul = str(
                book.get("judul", "")
            ).lower()

            penulis = str(
                book.get("penulis", "")
            ).lower()

            kategori_buku = str(
                book.get("kategori", "")
            )

            cocok_search = (
                keyword in judul or keyword in penulis
            )

            cocok_kategori = (
                kategori == "Semua Kategori"
                or kategori == kategori_buku
            )

            if cocok_search and cocok_kategori:
                filtered.append(book)

        row = 0
        col = 0

        for book in filtered:
            card = QFrame()
            card.setObjectName("module_card")

            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 18, 18, 18)
            layout.setSpacing(10)

            title = QLabel(
                f"📘 {book.get('judul', '-')}"
            )
            title.setStyleSheet(
                "font-size:16px; font-weight:bold;"
            )

            author = QLabel(
                f"Penulis: {book.get('penulis', '-')}"
            )

            category = QLabel(
                f"Kategori: {book.get('kategori', '-')}"
            )

            stock = QLabel(
                f"Stok: {book.get('stok', 0)}"
            )

            status = QLabel()

            if book.get("stok", 0) > 0:
                status.setText("✅ Tersedia")
                status.setStyleSheet(
                    "color:green; font-weight:bold;"
                )
            else:
                status.setText("❌ Stok Habis")
                status.setStyleSheet(
                    "color:red; font-weight:bold;"
                )

            button_layout = QHBoxLayout()

            detail_btn = QPushButton("Detail")
            borrow_btn = QPushButton("Pinjam")

            if book.get("stok", 0) <= 0:
                borrow_btn.setEnabled(False)

            detail_btn.clicked.connect(
                lambda _, b=book: self.show_detail(b)
            )

            borrow_btn.clicked.connect(
                lambda _, b=book: self.borrow_book(b)
            )

            button_layout.addWidget(detail_btn)
            button_layout.addWidget(borrow_btn)

            layout.addWidget(title)
            layout.addWidget(author)
            layout.addWidget(category)
            layout.addWidget(stock)
            layout.addWidget(status)
            layout.addLayout(button_layout)

            self.books_layout.addWidget(card, row, col)

            col += 1

            if col > 2:
                col = 0
                row += 1

    def show_detail(self, book):
        QMessageBox.information(
            self,
            "Detail Buku",
            f"Judul: {book.get('judul', '-')}\n\n"
            f"Penulis: {book.get('penulis', '-')}\n"
            f"Kategori: {book.get('kategori', '-')}\n"
            f"Stok: {book.get('stok', 0)}"
        )

    def borrow_book(self, book):
        try:
            tanggal_pinjam = date.today().isoformat()
            tanggal_kembali = (date.today() + timedelta(days=7)).isoformat()

            self.db.add_peminjaman(
                _member_id(self.user),
                book.get("id_buku") or book.get("id"),
                tanggal_pinjam,
                tanggal_kembali
            )

            QMessageBox.information(
                self,
                "Berhasil",
                "Buku berhasil dipinjam."
            )

            self.load_books()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Gagal",
                f"Peminjaman gagal.\n\n{e}"
            )

    def refresh(self):
        self.load_books()

class MemberLoansWidget(QWidget):
    def __init__(self, db, user: dict, history: bool = False):
        super().__init__()

        self.db = db
        self.user = _row_to_dict(user)
        self.history = history

        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        if self.history:
            title_text = "🕘 Riwayat Peminjaman"
            subtitle_text = "Halaman untuk melihat semua transaksi peminjaman anggota."
        else:
            title_text = "📖 Pinjaman Saya"
            subtitle_text = "Halaman untuk melihat buku yang masih dipinjam oleh anggota."

        title = QLabel(title_text)
        title.setStyleSheet("font-size:22px; font-weight:bold;")

        subtitle = QLabel(subtitle_text)
        subtitle.setWordWrap(True)

        top_bar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul buku...")

        self.filter_status = QComboBox()
        self.filter_status.addItems([
            "Semua",
            "Dipinjam",
            "Terlambat",
            "Dikembalikan"
        ])

        search_btn = QPushButton("Cari")
        refresh_btn = QPushButton("Refresh")

        search_btn.clicked.connect(self.load_loans)
        refresh_btn.clicked.connect(self.refresh)

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.filter_status)
        top_bar.addWidget(search_btn)
        top_bar.addWidget(refresh_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()

        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setSpacing(14)

        self.scroll.setWidget(self.container)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(top_bar)
        root.addWidget(self.scroll)

        self.load_loans()

    def load_loans(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        keyword = self.search_input.text().strip()
        status_filter = self.filter_status.currentText()

        if self.history:
            status = status_filter
        else:
            status = "Aktif"

        loans = self.db.get_user_peminjaman(
            _member_id(self.user),
            keyword,
            status
        )

        loans = [_row_to_dict(loan) for loan in loans]

        for loan in loans:
            judul = str(loan.get("judul", "")).lower()
            status = loan.get("status", "-")

            cocok_search = keyword.lower() in judul

            cocok_status = (
                status_filter == "Semua"
                or status == status_filter
                or not self.history
            )

            if cocok_search and cocok_status:
                card = QFrame()
                card.setObjectName("module_card")

                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(18, 18, 18, 18)
                card_layout.setSpacing(8)

                judul_label = QLabel(
                    f"📚 {loan.get('judul', '-')}"
                )
                judul_label.setStyleSheet(
                    "font-size:16px; font-weight:bold;"
                )

                status_label = QLabel(
                    f"Status: {status}"
                )

                tanggal_pinjam = QLabel(
                    f"Tanggal Pinjam: {loan.get('tanggal_pinjam', '-')}"
                )

                tanggal_kembali = QLabel(
                    f"Tanggal Kembali: {loan.get('tanggal_kembali', '-')}"
                )

                denda = QLabel(
                    f"Denda: Rp {loan.get('denda', 0)}"
                )

                if status == "Terlambat":
                    status_label.setStyleSheet(
                        "color:red; font-weight:bold;"
                    )

                elif status == "Dipinjam":
                    status_label.setStyleSheet(
                        "color:orange; font-weight:bold;"
                    )

                elif status == "Dikembalikan":
                    status_label.setStyleSheet(
                        "color:green; font-weight:bold;"
                    )

                card_layout.addWidget(judul_label)
                card_layout.addWidget(status_label)
                card_layout.addWidget(tanggal_pinjam)
                card_layout.addWidget(tanggal_kembali)
                card_layout.addWidget(denda)

                self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def refresh(self):
        self.load_loans()


class MemberProfileWidget(QWidget):
    def __init__(self, db, user: dict):
        super().__init__()

        self.db = db
        self.user = _row_to_dict(user)

        self.setObjectName("page")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("👤 Profil Anggota")
        title.setStyleSheet(
            "font-size:20px; font-weight:bold;"
        )

        subtitle = QLabel(
            "Halaman informasi akun peminjam."
        )

        card = QFrame()
        card.setObjectName("module_card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        nama = QLabel(
            f"Nama Lengkap: {self.user.get('nama_lengkap', '-')}"
        )

        username = QLabel(
            f"Username: {self.user.get('username', '-')}"
        )

        role = QLabel(
            f"Role: {self.user.get('role', '-')}"
        )

        info = QLabel(
            "Anggota hanya dapat melihat dan mengubah profilnya sendiri."
        )

        layout.addWidget(nama)
        layout.addWidget(username)
        layout.addWidget(role)
        layout.addWidget(info)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(card)
        root.addStretch()

    def refresh(self):
        pass