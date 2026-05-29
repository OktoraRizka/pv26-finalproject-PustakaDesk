"""
PustakaDesk — ui_main.py
Core main window: sidebar, menu, stacked page, dan navigasi role-based.

Struktur utama tetap sama:
- Login tetap dari ui_login.py
- MainWindow tetap pusat navigasi
- Admin memakai halaman operasional
- Anggota/peminjam memakai halaman katalog yang lebih stylish lewat ui_member.py
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


class ModulePlaceholder(QWidget):
    """Halaman sementara yang berisi arahan pekerjaan modul."""

    def __init__(self, icon, title, desc, owner, todos=None):
        super().__init__()
        self.setObjectName("page")
        self.icon = icon
        self.title = title
        self.desc = desc
        self.owner = owner
        self.todos = todos or [
            "Buat toolbar pencarian/filter sesuai kebutuhan modul.",
            "Buat area data utama, bisa tabel, card, atau form sesuai role pengguna.",
            "Hubungkan tombol aksi ke database dan logic yang sudah tersedia.",
            "Tambahkan refresh data dan validasi input."
        ]

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 26)
        root.setSpacing(18)

        header = QFrame()
        header.setObjectName("page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 18)
        header_layout.setSpacing(14)

        icon_box = QLabel(icon)
        icon_box.setObjectName("page_icon")
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(48, 48)

        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("page_title")
        lbl_desc = QLabel(desc)
        lbl_desc.setObjectName("subtitle_label")
        lbl_desc.setWordWrap(True)
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)

        header_layout.addWidget(icon_box)
        header_layout.addLayout(title_box, 1)
        root.addWidget(header)

        body = QFrame()
        body.setObjectName("module_card")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 24, 26, 24)
        body_layout.setSpacing(12)

        lbl = QLabel(f"{icon}  Template Modul {title}")
        lbl.setObjectName("module_title")

        note = QLabel(
            f"Bagian ini belum dibuat final dan disiapkan untuk {owner}. "
            "Tampilan core, menu, sidebar, dan role-based navigation sudah siap. "
            "Pengembang berikutnya tinggal mengisi isi halaman ini."
        )
        note.setObjectName("module_note")
        note.setWordWrap(True)

        todo_text = "Yang perlu dibuat:\n" + "\n".join(f"• {item}" for item in self.todos)
        todo = QLabel(todo_text)
        todo.setObjectName("module_todo")
        todo.setWordWrap(True)

        body_layout.addWidget(lbl)
        body_layout.addWidget(note)
        body_layout.addWidget(todo)
        body_layout.addStretch()
        root.addWidget(body, 1)

    def refresh(self):
        pass


def _nav_btn(icon, label):
    btn = QPushButton(f"{icon}   {label}")
    btn.setObjectName("nav_button")
    btn.setCheckable(True)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(42)
    return btn


class MainWindow(QMainWindow):
    def __init__(self, db, user: dict, app, load_stylesheet_fn, dark=False):
        super().__init__()
        self.db = db
        self.user = user
        self.app = app
        self.load_stylesheet = load_stylesheet_fn
        self._dark = dark
        self.role = (self.user.get("role") or "anggota").lower()
        self.is_admin = self.role == "admin"

        title_role = "Admin" if self.is_admin else "Peminjam"
        self.setWindowTitle(f"PustakaDesk — {title_role}")
        self.setMinimumSize(1050, 650)
        self.resize(1180, 700)
        self._build_ui()
        self._build_menu()
        self._build_statusbar()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("main_root")
        self.setCentralWidget(central)

        h = QHBoxLayout(central)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar" if self.is_admin else "member_sidebar")
        sidebar.setFixedWidth(238)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(14, 16, 14, 14)
        sb.setSpacing(10)

        brand = QFrame()
        brand.setObjectName("sidebar_brand" if self.is_admin else "member_sidebar_brand")
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(12, 12, 12, 12)
        brand_layout.setSpacing(10)

        logo = QLabel("📚")
        logo.setObjectName("brand_icon")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(40, 40)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        lbl_app = QLabel("PustakaDesk")
        lbl_app.setObjectName("sidebar_app_name")
        lbl_sub = QLabel("Admin Panel" if self.is_admin else "Library Portal")
        lbl_sub.setObjectName("sidebar_app_sub")
        brand_text.addWidget(lbl_app)
        brand_text.addWidget(lbl_sub)

        brand_layout.addWidget(logo)
        brand_layout.addLayout(brand_text)
        sb.addWidget(brand)

        user_card = QFrame()
        user_card.setObjectName("sidebar_user_card" if self.is_admin else "member_user_card")
        uc = QVBoxLayout(user_card)
        uc.setContentsMargins(12, 10, 12, 10)
        uc.setSpacing(2)
        role_text = "ADMIN" if self.is_admin else "PEMINJAM"
        lbl_role = QLabel(role_text)
        lbl_role.setObjectName("sidebar_user_role")
        lbl_name = QLabel(self.user.get("nama_lengkap") or self.user.get("username") or "User")
        lbl_name.setObjectName("sidebar_user_name")
        uc.addWidget(lbl_role)
        uc.addWidget(lbl_name)
        sb.addWidget(user_card)

        section = QLabel("MENU ADMIN" if self.is_admin else "MENU PEMINJAM")
        section.setObjectName("sidebar_section_label")
        sb.addWidget(section)

        self._stack = QStackedWidget()
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        nav_items = self._nav_items()
        self._nav_index = {}
        for i, (icon, label) in enumerate(nav_items):
            btn = _nav_btn(icon, label)
            self._btn_group.addButton(btn, i)
            sb.addWidget(btn)
            self._nav_index[label] = i
            self._stack.addWidget(self._make_page(label))

        self._btn_group.buttons()[0].setChecked(True)
        self._btn_group.idClicked.connect(self._stack.setCurrentIndex)

        sb.addStretch()

        logout = QPushButton("🚪   Logout")
        logout.setObjectName("btn_logout_sidebar")
        logout.setCursor(Qt.PointingHandCursor)
        logout.setMinimumHeight(42)
        logout.clicked.connect(self._on_logout)
        sb.addWidget(logout)

        h.addWidget(sidebar)
        h.addWidget(self._stack, 1)

    def _nav_items(self):
        if self.is_admin:
            return [
                ("🏠", "Dashboard"),
                ("📚", "Katalog Buku"),
                ("👥", "Manajemen User"),
                ("📋", "Peminjaman"),
                ("📊", "Laporan"),
            ]
        return [
            ("✨", "Beranda"),
            ("🔎", "Cari Buku"),
            ("📖", "Pinjaman Saya"),
            ("🕘", "Riwayat"),
            ("👤", "Profil"),
        ]

    def _make_page(self, label: str) -> QWidget:
        if not self.is_admin:
            try:
                from ui.ui_member import (
                    MemberHomeWidget, MemberCatalogWidget,
                    MemberLoansWidget, MemberProfileWidget
                )
                if label == "Beranda":
                    return MemberHomeWidget(self.db, self.user, self._go_to)
                if label == "Cari Buku":
                    return MemberCatalogWidget(self.db, self.user)
                if label == "Pinjaman Saya":
                    return MemberLoansWidget(self.db, self.user, history=False)
                if label == "Riwayat":
                    return MemberLoansWidget(self.db, self.user, history=True)
                if label == "Profil":
                    return MemberProfileWidget(self.db, self.user)
            except Exception as e:
                return ModulePlaceholder("⚠️", label, f"Halaman peminjam gagal dimuat: {e}", "Person 2/3")

        admin_modules = {
            "Dashboard": {
                "icon": "🏠",
                "desc": "Template dashboard admin. Statistik dan grafik belum dibuat final.",
                "owner": "Person 3",
                "todos": [
                    "Buat stat card: total buku, anggota, peminjaman aktif, dan terlambat.",
                    "Ambil data dari db.get_dashboard_stats(), bukan angka dummy.",
                    "Tambahkan aktivitas terbaru atau grafik sederhana jika diperlukan.",
                    "Tambahkan tombol refresh dan pastikan data berubah setelah transaksi."
                ],
            },
            "Katalog Buku": {
                "icon": "📚",
                "desc": "Template modul pengelolaan data buku untuk admin.",
                "owner": "Person 2",
                "todos": [
                    "Buat tabel buku: Judul, Penulis, Penerbit, Tahun, Kategori, Tersedia, Total.",
                    "Tambahkan search judul/penulis, filter kategori, dan sort data.",
                    "Buat tombol Tambah, Edit, Hapus, dan Refresh.",
                    "Hubungkan form ke database/db_buku.py dan validasi stok tidak boleh negatif.",
                    "Warnai atau beri penanda untuk buku yang stoknya habis."
                ],
            },
            "Manajemen User": {
                "icon": "👥",
                "desc": "Template modul pengelolaan akun admin dan anggota.",
                "owner": "Person 2",
                "todos": [
                    "Buat tabel user: Nama Lengkap, Username, Role, dan status jika diperlukan.",
                    "Tambahkan search dan filter role admin/anggota.",
                    "Buat tombol Tambah, Edit, Hapus dengan konfirmasi.",
                    "Pastikan user yang masih punya pinjaman aktif tidak bisa dihapus sembarangan.",
                    "Gunakan hashing password jika modul login dikembangkan lebih lanjut."
                ],
            },
            "Peminjaman": {
                "icon": "📋",
                "desc": "Template modul transaksi peminjaman dan pengembalian.",
                "owner": "Person 3",
                "todos": [
                    "Buat tabel transaksi: Buku, Peminjam, Tanggal Pinjam, Jatuh Tempo, Dikembalikan, Status, Denda.",
                    "Tambahkan search buku/peminjam dan filter status.",
                    "Buat tombol Pinjam Buku dan Kembalikan Buku.",
                    "Hitung denda otomatis saat pengembalian terlambat.",
                    "Pastikan stok buku berkurang saat dipinjam dan bertambah saat dikembalikan."
                ],
            },
            "Laporan": {
                "icon": "📊",
                "desc": "Template modul laporan peminjaman dan katalog.",
                "owner": "Person 3",
                "todos": [
                    "Buat tab Laporan Peminjaman dan Laporan Katalog Buku.",
                    "Tambahkan filter periode dan status laporan.",
                    "Tampilkan preview data sebelum ekspor.",
                    "Hubungkan tombol Ekspor CSV/PDF ke utils/export.py.",
                    "Nama file ekspor dibuat otomatis dengan tanggal."
                ],
            },
        }
        data = admin_modules.get(label, {
            "icon": "🔧",
            "desc": "Template halaman yang belum dikembangkan.",
            "owner": "anggota tim",
            "todos": None,
        })
        return ModulePlaceholder(data["icon"], label, data["desc"], data["owner"], data.get("todos"))

    def _build_menu(self):
        mb = self.menuBar()

        menu_app = mb.addMenu("Aplikasi")
        act_logout = QAction("Logout dari akun", self)
        act_logout.triggered.connect(self._on_logout)
        act_exit = QAction("Keluar aplikasi", self)
        act_exit.triggered.connect(self.close)
        menu_app.addAction(act_logout)
        menu_app.addSeparator()
        menu_app.addAction(act_exit)

        menu_data = mb.addMenu("Data" if self.is_admin else "Navigasi")
        for label in self._nav_index.keys():
            act = QAction(label, self)
            act.triggered.connect(lambda checked=False, l=label: self._go_to(l))
            menu_data.addAction(act)

        menu_view = mb.addMenu("Tampilan")
        self.act_theme = QAction("Gunakan Tema Terang" if self._dark else "Gunakan Tema Gelap", self)
        self.act_theme.triggered.connect(self._toggle_theme)
        menu_view.addAction(self.act_theme)

        menu_help = mb.addMenu("Bantuan")
        act_about = QAction("Tentang PustakaDesk", self)
        act_about.triggered.connect(self._show_about)
        menu_help.addAction(act_about)

    def _build_statusbar(self):
        if self.is_admin:
            msg = "  Mode Admin • Person 1: Core/Login/Main UI • Person 2: Buku & User • Person 3: Dashboard/Peminjaman/Laporan"
        else:
            msg = "  Mode Peminjam • Beranda/Cari Buku/Pinjaman Saya/Riwayat/Profil • UI anggota terpisah dari admin"
        self.statusBar().showMessage(msg)

    def _go_to(self, label):
        idx = self._nav_index[label]
        self._stack.setCurrentIndex(idx)
        self._btn_group.button(idx).setChecked(True)
        widget = self._stack.widget(idx)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _toggle_theme(self):
        self._dark = not self._dark
        self.load_stylesheet(self.app, self._dark)
        self.act_theme.setText("Gunakan Tema Terang" if self._dark else "Gunakan Tema Gelap")

    def _on_logout(self):
        confirm = QMessageBox.question(self, "Logout", "Yakin ingin logout dari akun ini?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            from ui.ui_login import LoginWindow
            self._login = LoginWindow(self.db, self.app, self.load_stylesheet)
            self._login.show()
            self.close()

    def _show_about(self):
        QMessageBox.information(
            self,
            "Tentang PustakaDesk",
            "PustakaDesk — Sistem Manajemen Perpustakaan\n\n"
            "Aplikasi desktop PySide6 untuk mengelola katalog buku, anggota, peminjaman, pengembalian, dan laporan.\n\n"
            "Core awal sudah role-based: admin memakai UI operasional, sedangkan peminjam memakai UI katalog yang lebih nyaman."
        )
