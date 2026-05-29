"""
PustakaDesk — ui_member.py
Template halaman khusus anggota/peminjam.

Versi ini sengaja BELUM dibuat menjadi fitur final.
Tujuannya: menjaga UI role peminjam tetap berbeda dari admin, tetapi setiap halaman
masih berupa halaman arahan/tugas untuk dikerjakan anggota berikutnya.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
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
        """Disediakan agar aman dipanggil dari MainWindow, tetapi belum melakukan apa pun."""
        pass


class MemberHomeWidget(MemberTaskPage):
    def __init__(self, db, user: dict, go_to_callback=None):
        self.db = db
        self.user = user
        self.go_to = go_to_callback
        super().__init__(
            icon="✨",
            title="Beranda Peminjam",
            subtitle="Halaman awal anggota. Nantinya berisi ringkasan dan pintasan utama peminjam.",
            owner="Person 2/3",
            tasks=[
                "Buat hero sederhana berisi sapaan anggota dan search cepat buku.",
                "Tampilkan ringkasan kecil: pinjaman aktif, terlambat, riwayat, dan buku tersedia.",
                "Tambahkan rekomendasi buku atau buku terbaru dalam bentuk card, tetapi datanya harus dari database.",
                "Sediakan tombol cepat ke Cari Buku dan Pinjaman Saya.",
                "Jangan pakai data dummy final; gunakan database/db_buku.py saat modul sudah dikerjakan."
            ],
            note="Catatan: halaman ini boleh lebih stylish dari admin, tapi tetap jangan terlalu ramai karena hanya portal anggota."
        )


class MemberCatalogWidget(MemberTaskPage):
    def __init__(self, db, user: dict):
        self.db = db
        self.user = user
        super().__init__(
            icon="🔎",
            title="Cari Buku",
            subtitle="Halaman katalog untuk mencari buku dan mengajukan peminjaman.",
            owner="Person 2",
            tasks=[
                "Buat search bar untuk judul/penulis dan filter kategori.",
                "Tampilkan daftar buku sebagai card atau grid katalog yang rapi.",
                "Ambil data dari db.get_all_books() dan kategori dari db.get_kategori_list().",
                "Buat tombol Detail untuk menampilkan informasi buku.",
                "Buat tombol Pinjam yang hanya aktif jika stok tersedia dan terhubung ke proses peminjaman.",
                "Setelah peminjaman berhasil, stok dan daftar buku harus refresh otomatis."
            ],
            note="Style katalog peminjam boleh lebih visual daripada tabel admin, tetapi alurnya tetap sederhana: cari → detail → pinjam."
        )


class MemberLoansWidget(MemberTaskPage):
    def __init__(self, db, user: dict, history: bool = False):
        self.db = db
        self.user = user
        self.history = history
        if history:
            super().__init__(
                icon="🕘",
                title="Riwayat Peminjaman",
                subtitle="Halaman untuk melihat semua transaksi peminjaman anggota.",
                owner="Person 3",
                tasks=[
                    "Tampilkan seluruh riwayat pinjam anggota dari database.",
                    "Tambahkan filter status: Semua, Dipinjam, Terlambat, Dikembalikan.",
                    "Tambahkan search berdasarkan judul buku.",
                    "Gunakan card/list yang ringan, bukan tabel admin penuh.",
                    "Tampilkan tanggal pinjam, tanggal kembali, status, dan denda jika ada."
                ],
                note="Riwayat hanya untuk membaca data; aksi pengembalian tetap lebih cocok di modul admin/petugas."
            )
        else:
            super().__init__(
                icon="📖",
                title="Pinjaman Saya",
                subtitle="Halaman untuk melihat buku yang masih dipinjam oleh anggota.",
                owner="Person 3",
                tasks=[
                    "Tampilkan hanya pinjaman aktif milik anggota yang login.",
                    "Tambahkan indikator status: Dipinjam atau Terlambat.",
                    "Tampilkan tanggal jatuh tempo agar anggota tahu kapan harus mengembalikan buku.",
                    "Tambahkan search kecil untuk judul buku jika data sudah banyak.",
                    "Jangan beri tombol edit/hapus di sisi peminjam; perubahan transaksi dilakukan admin."
                ],
                note="Halaman ini harus terasa informatif, bukan operasional. Fokusnya memberi tahu status pinjaman anggota."
            )


class MemberProfileWidget(MemberTaskPage):
    def __init__(self, db, user: dict):
        self.db = db
        self.user = user
        super().__init__(
            icon="👤",
            title="Profil Anggota",
            subtitle="Halaman informasi akun peminjam.",
            owner="Person 2",
            tasks=[
                "Tampilkan nama lengkap, username, role, dan informasi kontak jika ada di database.",
                "Siapkan tombol Edit Profil jika struktur database profil sudah ditambahkan.",
                "Tambahkan validasi input untuk nama, username, dan kontak.",
                "Buat opsi ganti password jika dibutuhkan, tetapi jangan tampilkan password lama.",
                "Pastikan anggota hanya bisa melihat/mengubah profilnya sendiri."
            ],
            note="Profil cukup sederhana. Jangan dibuat seperti halaman admin, karena anggota hanya butuh identitas dan pengaturan dasar."
        )
