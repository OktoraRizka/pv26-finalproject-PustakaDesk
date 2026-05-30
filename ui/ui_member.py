"""
PustakaDesk — ui_member.py
Template halaman khusus anggota/peminjam.

Versi ini sengaja BELUM dibuat menjadi fitur final.
Tujuannya: menjaga UI role peminjam tetap berbeda dari admin, tetapi setiap halaman
masih berupa halaman arahan/tugas untuk dikerjakan anggota berikutnya.
"""
from PySide6.QtWidgets import (
     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,  QLineEdit,
    QPushButton, QScrollArea, QGridLayout, QMessageBox, QComboBox
     )
from PySide6.QtCore import Qt


class MemberTaskPage(QWidget):
    """Halaman kosong terarah untuk modul peminjam yang belum dikerjakan."""

    def __init__(self, icon: str, title: str, subtitle: str, owner: str, tasks: list[str], note: str = ""):
        super().__init__()
        self.setObjectName("page")
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.owner = owner
        self.tasks = tasks
        self.note = note
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 24)
        root.setSpacing(16)

        header = QFrame()
        header.setObjectName("member_page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 18)
        header_layout.setSpacing(14)

        icon_box = QLabel(self.icon)
        icon_box.setObjectName("member_stat_icon")
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(48, 48)

        text_box = QVBoxLayout()
        text_box.setSpacing(5)
        title = QLabel(self.title)
        title.setObjectName("member_page_title")
        subtitle = QLabel(self.subtitle)
        subtitle.setObjectName("member_page_subtitle")
        subtitle.setWordWrap(True)
        text_box.addWidget(title)
        text_box.addWidget(subtitle)

        header_layout.addWidget(icon_box)
        header_layout.addLayout(text_box, 1)
        root.addWidget(header)

        body = QFrame()
        body.setObjectName("module_card")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 24, 26, 24)
        body_layout.setSpacing(12)

        module_title = QLabel(f"{self.icon}  Template Modul {self.title}")
        module_title.setObjectName("module_title")

        module_note = QLabel(
            f"Halaman ini belum dibuat final. Bagian ini disiapkan untuk {self.owner}, "
            "supaya pengembang berikutnya langsung tahu isi yang perlu dibangun tanpa mengubah core navigasi."
        )
        module_note.setObjectName("module_note")
        module_note.setWordWrap(True)

        todo_text = "Yang perlu dibuat:\n" + "\n".join(f"• {task}" for task in self.tasks)
        todo = QLabel(todo_text)
        todo.setObjectName("module_todo")
        todo.setWordWrap(True)

        body_layout.addWidget(module_title)
        body_layout.addWidget(module_note)
        body_layout.addWidget(todo)

        if self.note:
            extra = QLabel(self.note)
            extra.setObjectName("module_note")
            extra.setWordWrap(True)
            body_layout.addWidget(extra)

        body_layout.addStretch()
        root.addWidget(body, 1)

    def refresh(self):
        pass


class MemberHomeWidget(QWidget):
    def __init__(self, db, user: dict, go_to_callback=None):
        super().__init__()

        self.db = db
        self.user = user
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

        if hasattr(self.db, "get_member_active_loans"):
            active_loans = self.db.get_member_active_loans(
                self.user.get("id")
            )
            total_active = len(active_loans)

            for loan in active_loans:
                if loan.get("status") == "Terlambat":
                    total_late += 1

        if hasattr(self.db, "get_member_history"):
            total_history = len(
                self.db.get_member_history(
                    self.user.get("id")
                )
            )

        if hasattr(self.db, "get_all_books"):
            total_books = len(
                self.db.get_all_books()
            )

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
                lambda: self.go_to("member_catalog")
            )

            loans_btn.clicked.connect(
                lambda: self.go_to("member_loans")
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
            books = self.db.get_all_books()[:5]

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
        self.user = user

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
            books = self.db.get_all_books()

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
        if hasattr(self.db, "borrow_book"):
            success = self.db.borrow_book(
                self.user.get("id"),
                book.get("id")
            )

            if success:
                QMessageBox.information(
                    self,
                    "Berhasil",
                    "Buku berhasil dipinjam."
                )

                self.load_books()

            else:
                QMessageBox.warning(
                    self,
                    "Gagal",
                    "Peminjaman gagal."
                )

    def refresh(self):
        self.load_books()

class MemberLoansWidget(QWidget):
    def __init__(self, db, user: dict, history: bool = False):
        super().__init__()

        self.db = db
        self.user = user
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

        keyword = self.search_input.text().lower()
        status_filter = self.filter_status.currentText()

        if self.history:
            loans = self.db.get_member_history(
                self.user["id_user"]
            )
        else:
            loans = self.db.get_member_active_loans(
                self.user["id_user"]
            )

        for loan in loans:
            judul = loan.get("judul", "").lower()
            status = loan.get("status", "-")

            cocok_search = keyword in judul

            cocok_status = (
                status_filter == "Semua"
                or status == status_filter
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
        self.user = user

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