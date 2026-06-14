"""
PustakaDesk — DatabaseBuku
Core layer: inisialisasi tabel, CRUD User / Books / Peminjaman dengan SQLite.
"""
import sqlite3
import hashlib
import os
from datetime import date, datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "database_buku.db")


def _hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


class DatabaseBuku:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    #  Koneksi

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    #  Inisialisasi Skema

    def initialize(self):
        """Buat tabel jika belum ada, lalu seed data awal."""
        with self.get_connection() as conn:
            conn.executescript("""
                --  Tabel User 
                CREATE TABLE IF NOT EXISTS user (
                    id_user      INTEGER PRIMARY KEY AUTOINCREMENT,
                    username     VARCHAR(100) NOT NULL UNIQUE,
                    password     VARCHAR(100) NOT NULL,
                    nama_lengkap VARCHAR(100) NOT NULL,
                    role         VARCHAR(50)  NOT NULL DEFAULT 'anggota',
                    profile_image_path TEXT    DEFAULT '',
                    is_active    INTEGER      NOT NULL DEFAULT 1,
                    deleted_at   TEXT
                );

                --  Tabel Books 
                CREATE TABLE IF NOT EXISTS books (
                    id_buku      INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul        VARCHAR(100) NOT NULL,
                    penulis      VARCHAR(100) NOT NULL,
                    penerbit     VARCHAR(100),
                    tahun_terbit INTEGER,
                    kategori     VARCHAR(50)  NOT NULL DEFAULT 'Umum',
                    stok         INTEGER      NOT NULL DEFAULT 1,
                    total_stok   INTEGER      NOT NULL DEFAULT 1,
                    image_path   TEXT         DEFAULT '',
                    deskripsi    TEXT         DEFAULT ''
                );

                --  Tabel Peminjaman
                CREATE TABLE IF NOT EXISTS peminjaman (
                    id_peminjaman  INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_user        INTEGER NOT NULL,
                    id_buku        INTEGER NOT NULL,
                    tanggal_pinjam DATE    NOT NULL,
                    tanggal_kembali DATE   NOT NULL,
                    tanggal_kembali_aktual DATE,
                    status         VARCHAR(50) NOT NULL DEFAULT 'Dipinjam',
                    denda          REAL        NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (id_user) REFERENCES user(id_user)   ON DELETE RESTRICT,
                    FOREIGN KEY (id_buku) REFERENCES books(id_buku)  ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_pinjam_user  ON peminjaman(id_user);
                CREATE INDEX IF NOT EXISTS idx_pinjam_buku  ON peminjaman(id_buku);
                CREATE INDEX IF NOT EXISTS idx_pinjam_status ON peminjaman(status);
            """)
            self._ensure_schema(conn)
            self._seed(conn)
            self._seed_book_descriptions(conn)

    def _ensure_schema(self, conn: sqlite3.Connection):
        """Migrasi ringan agar database lama tetap bisa dipakai."""
        book_columns = [row[1] for row in conn.execute("PRAGMA table_info(books)").fetchall()]
        if "image_path" not in book_columns:
            conn.execute("ALTER TABLE books ADD COLUMN image_path TEXT DEFAULT ''")
        if "deskripsi" not in book_columns:
            conn.execute("ALTER TABLE books ADD COLUMN deskripsi TEXT DEFAULT ''")

        user_columns = [row[1] for row in conn.execute("PRAGMA table_info(user)").fetchall()]
        if "profile_image_path" not in user_columns:
            conn.execute("ALTER TABLE user ADD COLUMN profile_image_path TEXT DEFAULT ''")
        if "is_active" not in user_columns:
            conn.execute("ALTER TABLE user ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
        if "deleted_at" not in user_columns:
            conn.execute("ALTER TABLE user ADD COLUMN deleted_at TEXT")

    def _seed_book_descriptions(self, conn: sqlite3.Connection):
        """Isi deskripsi default untuk data contoh jika kolom masih kosong."""
        sample_descriptions = {
            "Laskar Pelangi": "Novel tentang perjuangan anak-anak Belitung dalam mengejar pendidikan, persahabatan, dan mimpi di tengah keterbatasan.",
            "Bumi Manusia": "Kisah Minke yang menggambarkan kehidupan sosial, pendidikan, dan ketidakadilan pada masa kolonial Hindia Belanda.",
            "Atomic Habits": "Buku pengembangan diri yang membahas cara membangun kebiasaan kecil secara konsisten untuk menghasilkan perubahan besar.",
            "Clean Code": "Panduan praktis untuk menulis kode yang mudah dibaca, dirawat, dan dikembangkan dalam proyek perangkat lunak.",
            "Python Crash Course": "Buku pengantar Python yang menyajikan dasar pemrograman dan latihan proyek sederhana untuk pemula.",
            "Sapiens": "Pembahasan ringkas tentang sejarah manusia, perkembangan peradaban, budaya, dan perubahan besar dalam kehidupan Homo sapiens.",
            "Thinking, Fast and Slow": "Kajian populer tentang cara manusia berpikir, mengambil keputusan, serta bias yang sering memengaruhi penilaian sehari-hari.",
        }
        for judul, deskripsi in sample_descriptions.items():
            conn.execute(
                "UPDATE books SET deskripsi=? WHERE judul=? AND (deskripsi IS NULL OR TRIM(deskripsi)='')",
                (deskripsi, judul)
            )

    def _seed(self, conn: sqlite3.Connection):
        if conn.execute("SELECT COUNT(*) FROM user").fetchone()[0] > 0:
            return

        # Default admin
        conn.execute(
            "INSERT INTO user (username, password, nama_lengkap, role) VALUES (?,?,?,?)",
            ("admin", _hash_password("admin123"), "Administrator", "admin")
        )
        # Sample anggota. Data awal cukup satu anggota agar database demo tetap bersih.
        sample_users = [
            ("budi", _hash_password("budi123"), "Budi Santoso", "anggota"),
        ]
        conn.executemany(
            "INSERT INTO user (username, password, nama_lengkap, role) VALUES (?,?,?,?)",
            sample_users
        )

        # Sample buku
        sample_books = [
            ("Laskar Pelangi",          "Andrea Hirata",       "Bentang Pustaka",   2005, "Novel",       3, 3),
            ("Bumi Manusia",            "Pramoedya A. Toer",   "Hasta Mitra",       1980, "Novel",       2, 2),
            ("Atomic Habits",           "James Clear",         "Penguin Books",     2018, "Self-Help",   4, 4),
            ("Clean Code",              "Robert C. Martin",    "Prentice Hall",     2008, "Pemrograman", 2, 2),
            ("Python Crash Course",     "Eric Matthes",        "No Starch Press",   2023, "Pemrograman", 2, 2),
            ("Sapiens",                 "Yuval Noah Harari",   "Harper",            2015, "Sejarah",     3, 3),
            ("Thinking, Fast and Slow", "Daniel Kahneman",     "Farrar & Straus",   2011, "Psikologi",   3, 3),
        ]
        conn.executemany(
            "INSERT INTO books (judul,penulis,penerbit,tahun_terbit,kategori,stok,total_stok) "
            "VALUES (?,?,?,?,?,?,?)",
            sample_books
        )

    # USER CRUD

    def login(self, username: str, password: str):
        """Return Row user jika kredensial valid, else None."""
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM user WHERE username=? AND password=? AND is_active=1",
                (username.strip(), _hash_password(password))
            ).fetchone()

    def get_all_users(self, search: str = "", role: str = "Semua",
                      sort_col: str = "nama_lengkap", sort_order: str = "ASC"):
        safe = {"nama_lengkap", "username", "role"}
        if sort_col not in safe:
            sort_col = "nama_lengkap"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "ASC"

        q = ("SELECT id_user, username, nama_lengkap, role "
             "FROM user WHERE is_active=1 "
             "AND (username LIKE ? OR nama_lengkap LIKE ?)")
        p = [f"%{search}%", f"%{search}%"]
        if role != "Semua":
            q += " AND role = ?"
            p.append(role)
        q += f" ORDER BY {sort_col} {sort_order}"
        with self.get_connection() as conn:
            return conn.execute(q, p).fetchall()

    def get_user_by_id(self, id_user: int):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM user WHERE id_user=? AND is_active=1", (id_user,)
            ).fetchone()

    def add_user(self, username: str, password: str,
                 nama_lengkap: str, role: str = "anggota"):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO user (username, password, nama_lengkap, role) VALUES (?,?,?,?)",
                (username.strip(), _hash_password(password), nama_lengkap.strip(), role)
            )

    def update_user(self, id_user: int, username: str,
                    nama_lengkap: str, role: str,
                    new_password: str = "", profile_image_path=None):
        """Update akun. profile_image_path=None berarti foto lama tetap dipakai."""
        fields = ["username=?", "nama_lengkap=?", "role=?"]
        params = [username.strip(), nama_lengkap.strip(), role]

        if new_password:
            fields.append("password=?")
            params.append(_hash_password(new_password))

        if profile_image_path is not None:
            fields.append("profile_image_path=?")
            params.append(profile_image_path or "")

        params.append(id_user)
        with self.get_connection() as conn:
            conn.execute(
                f"UPDATE user SET {', '.join(fields)} WHERE id_user=?",
                params
            )

    def delete_user(self, id_user: int):
        """Hapus akun tanpa merusak riwayat peminjaman.

        - Akun tanpa transaksi dihapus secara permanen.
        - Akun yang sudah memiliki riwayat selesai dinonaktifkan (soft delete),
          sehingga foreign key dan nama pada laporan lama tetap tersedia.
        - Akun dengan pinjaman aktif tetap tidak boleh dihapus.

        Return ``"hard"`` atau ``"soft"`` untuk kebutuhan pesan UI.
        """
        with self.get_connection() as conn:
            user = conn.execute(
                "SELECT id_user, username, is_active FROM user WHERE id_user=?",
                (id_user,)
            ).fetchone()
            if not user or not user["is_active"]:
                raise ValueError("User tidak ditemukan atau sudah dihapus.")

            active = conn.execute(
                "SELECT COUNT(*) FROM peminjaman "
                "WHERE id_user=? AND status IN "
                "('Dipinjam','Terlambat','Konfirmasi','Menunggu Persetujuan')",
                (id_user,)
            ).fetchone()[0]
            if active > 0:
                raise ValueError(
                    "User masih memiliki pinjaman atau pengajuan aktif. "
                    "Selesaikan transaksi tersebut sebelum menghapus akun."
                )

            total_history = conn.execute(
                "SELECT COUNT(*) FROM peminjaman WHERE id_user=?",
                (id_user,)
            ).fetchone()[0]

            if total_history == 0:
                conn.execute("DELETE FROM user WHERE id_user=?", (id_user,))
                return "hard"

            # Username dibuat internal agar username lama dapat dipakai untuk
            # registrasi baru. Nama lengkap dipertahankan untuk riwayat/laporan.
            deleted_at = datetime.now().isoformat(timespec="seconds")
            internal_username = f"__deleted_{id_user}_{int(datetime.now().timestamp())}"
            conn.execute(
                "UPDATE user SET username=?, password=?, is_active=0, "
                "deleted_at=?, profile_image_path='' WHERE id_user=?",
                (internal_username, _hash_password(internal_username), deleted_at, id_user)
            )
            return "soft"

    # BOOKS CRUD

    def get_all_books(self, search: str = "", kategori: str = "Semua",
                      sort_col: str = "judul", sort_order: str = "ASC"):
        safe = {"judul", "penulis", "kategori", "tahun_terbit", "stok"}
        if sort_col not in safe:
            sort_col = "judul"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "ASC"

        q = ("SELECT id_buku, judul, penulis, penerbit, tahun_terbit, "
             "kategori, stok, total_stok, image_path, deskripsi FROM books "
             "WHERE (judul LIKE ? OR penulis LIKE ?)")
        p = [f"%{search}%", f"%{search}%"]
        if kategori != "Semua":
            q += " AND kategori = ?"
            p.append(kategori)
        q += f" ORDER BY {sort_col} {sort_order}"
        with self.get_connection() as conn:
            return conn.execute(q, p).fetchall()

    def get_book_by_id(self, id_buku: int):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM books WHERE id_buku=?", (id_buku,)
            ).fetchone()

    def get_available_books(self):
        """Buku dengan stok > 0, untuk ComboBox peminjaman."""
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT id_buku, judul, penulis, stok "
                "FROM books WHERE stok > 0 ORDER BY judul"
            ).fetchall()

    def get_kategori_list(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT kategori FROM books ORDER BY kategori"
            ).fetchall()
            return [r[0] for r in rows]

    def add_book(self, judul: str, penulis: str, penerbit: str,
                    tahun_terbit: int, kategori: str, stok: int,
                    image_path: str = "", deskripsi: str = ""):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO books (judul,penulis,penerbit,tahun_terbit,kategori,stok,total_stok,image_path,deskripsi) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (judul, penulis, penerbit, tahun_terbit, kategori, stok, stok, image_path or "", deskripsi.strip())
            )

    def update_book(self, id_buku: int, judul: str, penulis: str,
                    penerbit: str, tahun_terbit: int,
                    kategori: str, total_stok: int,
                    image_path: str = "", deskripsi: str = ""):
        with self.get_connection() as conn:
            sedang_dipinjam = conn.execute(
                "SELECT COUNT(*) FROM peminjaman "
                "WHERE id_buku=? AND status IN ('Dipinjam','Terlambat','Konfirmasi','Menunggu Persetujuan')",
                (id_buku,)
            ).fetchone()[0]
            new_stok = max(0, total_stok - sedang_dipinjam)
            conn.execute(
                "UPDATE books SET judul=?,penulis=?,penerbit=?,tahun_terbit=?,"
                "kategori=?,stok=?,total_stok=?,image_path=?,deskripsi=? WHERE id_buku=?",
                (judul, penulis, penerbit, tahun_terbit,
                    kategori, new_stok, total_stok, image_path or "", deskripsi.strip(), id_buku)
            )

    def delete_book(self, id_buku: int):
        with self.get_connection() as conn:
            active = conn.execute(
                "SELECT COUNT(*) FROM peminjaman "
                "WHERE id_buku=? AND status IN ('Dipinjam','Terlambat','Konfirmasi','Menunggu Persetujuan')",
                (id_buku,)
            ).fetchone()[0]
            if active > 0:
                raise ValueError("Buku masih dipinjam, tidak bisa dihapus.")
            conn.execute("DELETE FROM books WHERE id_buku=?", (id_buku,))

    # PEMINJAMAN CRUD

    def get_all_peminjaman(self, search: str = "", status: str = "Semua",
                        sort_col: str = "tanggal_pinjam", sort_order: str = "DESC"):
        self.update_status_terlambat()
        safe = {"tanggal_pinjam", "tanggal_kembali", "status"}
        if sort_col not in safe:
            sort_col = "tanggal_pinjam"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "DESC"

        q = """
            SELECT p.id_peminjaman,
                    b.judul, b.penulis,
                    u.nama_lengkap, u.username,
                    p.tanggal_pinjam, p.tanggal_kembali,
                    p.tanggal_kembali_aktual,
                    p.status, CAST(p.denda AS INTEGER) AS denda
            FROM peminjaman p
            JOIN books b ON p.id_buku  = b.id_buku
            JOIN user  u ON p.id_user  = u.id_user
            WHERE (b.judul LIKE ? OR u.nama_lengkap LIKE ? OR u.username LIKE ?)
        """
        params = [f"%{search}%"] * 3
        if status == "Aktif":
            q += " AND p.status IN ('Dipinjam','Terlambat','Konfirmasi','Menunggu Persetujuan')"
        elif status == "Riwayat":
            q += " AND p.status = 'Dikembalikan'"
        elif status != "Semua":
            q += " AND p.status = ?"
            params.append(status)
        q += f" ORDER BY p.{sort_col} {sort_order}"
        with self.get_connection() as conn:
            return conn.execute(q, params).fetchall()

    def get_peminjaman_by_id(self, id_peminjaman: int):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM peminjaman WHERE id_peminjaman=?",
                (id_peminjaman,)
            ).fetchone()

    def _create_peminjaman(self, conn, id_user: int, id_buku: int,
                            tanggal_pinjam: str, tanggal_kembali: str,
                            status: str):
        """Simpan pinjaman/pengajuan dan reservasi satu salinan buku."""
        buku = conn.execute(
            "SELECT stok, judul FROM books WHERE id_buku=?", (id_buku,)
        ).fetchone()
        if not buku:
            raise ValueError("Buku tidak ditemukan.")
        if buku["stok"] <= 0:
            raise ValueError(f"Stok buku '{buku['judul']}' habis.")

        conn.execute(
            "INSERT INTO peminjaman "
            "(id_user,id_buku,tanggal_pinjam,tanggal_kembali,status) "
            "VALUES (?,?,?,?,?)",
            (id_user, id_buku, tanggal_pinjam, tanggal_kembali, status)
        )
        # Pengajuan berdurasi panjang ikut mereservasi salinan agar stok tidak
        # dapat dipesan oleh beberapa anggota pada waktu yang sama.
        conn.execute(
            "UPDATE books SET stok = stok - 1 WHERE id_buku=?", (id_buku,)
        )

    def add_peminjaman(self, id_user: int, id_buku: int,
                        tanggal_pinjam: str, tanggal_kembali: str):
        """Peminjaman langsung untuk durasi maksimal tujuh hari."""
        with self.get_connection() as conn:
            self._create_peminjaman(
                conn, id_user, id_buku, tanggal_pinjam, tanggal_kembali, "Dipinjam"
            )

    def add_pengajuan_peminjaman(self, id_user: int, id_buku: int,
                                 tanggal_pinjam: str, tanggal_kembali: str):
        """Pengajuan durasi lebih dari tujuh hari yang menunggu persetujuan admin."""
        with self.get_connection() as conn:
            self._create_peminjaman(
                conn, id_user, id_buku, tanggal_pinjam, tanggal_kembali,
                "Menunggu Persetujuan"
            )

    def setujui_pengajuan_peminjaman(self, id_peminjaman: int):
        """Admin menyetujui pengajuan. Stok sudah direservasi saat diajukan."""
        with self.get_connection() as conn:
            data = conn.execute(
                "SELECT status FROM peminjaman WHERE id_peminjaman=?",
                (id_peminjaman,)
            ).fetchone()
            if not data:
                raise ValueError("Data pengajuan tidak ditemukan.")
            if data["status"] != "Menunggu Persetujuan":
                raise ValueError("Data yang dipilih bukan pengajuan yang menunggu persetujuan.")
            conn.execute(
                "UPDATE peminjaman SET status='Dipinjam' WHERE id_peminjaman=?",
                (id_peminjaman,)
            )

    def tolak_pengajuan_peminjaman(self, id_peminjaman: int):
        """Admin menolak pengajuan dan mengembalikan stok yang direservasi."""
        with self.get_connection() as conn:
            data = conn.execute(
                "SELECT id_buku, status FROM peminjaman WHERE id_peminjaman=?",
                (id_peminjaman,)
            ).fetchone()
            if not data:
                raise ValueError("Data pengajuan tidak ditemukan.")
            if data["status"] != "Menunggu Persetujuan":
                raise ValueError("Data yang dipilih bukan pengajuan yang menunggu persetujuan.")
            conn.execute(
                "UPDATE peminjaman SET status='Ditolak' WHERE id_peminjaman=?",
                (id_peminjaman,)
            )
            conn.execute(
                "UPDATE books SET stok = MIN(total_stok, stok + 1) WHERE id_buku=?",
                (data["id_buku"],)
            )

    def ajukan_pengembalian(self, id_peminjaman: int,
                            tanggal_pengajuan: str,
                            denda_per_hari: int = 1000):
        """Anggota mengajukan pengembalian. Stok baru bertambah setelah admin konfirmasi."""
        with self.get_connection() as conn:
            p = conn.execute(
                "SELECT * FROM peminjaman WHERE id_peminjaman=?",
                (id_peminjaman,)
            ).fetchone()
            if not p:
                raise ValueError("Data peminjaman tidak ditemukan.")
            if p["status"] == "Dikembalikan":
                raise ValueError("Buku sudah dikembalikan sebelumnya.")
            if p["status"] == "Konfirmasi":
                raise ValueError("Pengembalian sudah diajukan dan masih menunggu konfirmasi admin.")
            if p["status"] == "Menunggu Persetujuan":
                raise ValueError("Peminjaman belum disetujui admin.")
            if p["status"] == "Ditolak":
                raise ValueError("Pengajuan peminjaman sudah ditolak.")

            due = date.fromisoformat(p["tanggal_kembali"])
            actual = date.fromisoformat(tanggal_pengajuan)
            hari_terlambat = max(0, (actual - due).days)
            denda = hari_terlambat * denda_per_hari

            conn.execute(
                "UPDATE peminjaman SET tanggal_kembali_aktual=?, "
                "status='Konfirmasi', denda=? WHERE id_peminjaman=?",
                (tanggal_pengajuan, denda, id_peminjaman)
            )
            return denda

    def kembalikan_buku(self, id_peminjaman: int,
                        tanggal_aktual: str, denda_per_hari: int = 1000):
        """Konfirmasi pengembalian + hitung denda otomatis."""
        with self.get_connection() as conn:
            p = conn.execute(
                "SELECT * FROM peminjaman WHERE id_peminjaman=?",
                (id_peminjaman,)
            ).fetchone()
            if not p:
                raise ValueError("Data peminjaman tidak ditemukan.")
            if p["status"] == "Dikembalikan":
                raise ValueError("Buku sudah dikembalikan sebelumnya.")
            if p["status"] in ("Menunggu Persetujuan", "Ditolak"):
                raise ValueError("Pengajuan ini belum menjadi peminjaman aktif.")

            # Jika anggota sudah mengajukan pengembalian, tanggal pengajuan dipakai sebagai tanggal aktual.
            actual_iso = p["tanggal_kembali_aktual"] or tanggal_aktual
            due = date.fromisoformat(p["tanggal_kembali"])
            ret = date.fromisoformat(actual_iso)
            hari_terlambat = max(0, (ret - due).days)
            denda = hari_terlambat * denda_per_hari

            conn.execute(
                "UPDATE peminjaman SET tanggal_kembali_aktual=?, "
                "status='Dikembalikan', denda=? WHERE id_peminjaman=?",
                (actual_iso, denda, id_peminjaman)
            )
            conn.execute(
                "UPDATE books SET stok = stok + 1 WHERE id_buku=?",
                (p["id_buku"],)
            )
            return denda

    def update_status_terlambat(self, denda_per_hari: int = 1000):
        """Tandai pinjaman yang melewati tanggal jatuh tempo sebagai Terlambat.

        Status yang diperbarui hanya Dipinjam/Terlambat. Status Konfirmasi tidak
        diubah, karena anggota sudah mengajukan pengembalian dan tinggal menunggu
        pemeriksaan admin.
        """
        today = date.today().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE peminjaman
                SET status='Terlambat',
                    denda = CAST((julianday(?) - julianday(tanggal_kembali)) AS INTEGER) * ?
                WHERE status IN ('Dipinjam','Terlambat')
                  AND tanggal_kembali < ?
                """,
                (today, denda_per_hari, today)
            )

    # STATS (untuk Dashboard)

    def get_dashboard_stats(self) -> dict:
        self.update_status_terlambat()
        with self.get_connection() as conn:
            return {
                "total_buku":     conn.execute("SELECT COUNT(*) FROM books").fetchone()[0],
                "total_anggota":  conn.execute(
                    "SELECT COUNT(*) FROM user WHERE role='anggota' AND is_active=1"
                ).fetchone()[0],
                "sedang_dipinjam": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman WHERE status IN ('Dipinjam','Terlambat','Konfirmasi')"
                ).fetchone()[0],
                "terlambat":      conn.execute(
                    "SELECT COUNT(*) FROM peminjaman WHERE status='Terlambat'"
                ).fetchone()[0],
                "aktivitas_terbaru": conn.execute("""
                    SELECT b.judul, u.nama_lengkap,
                            p.tanggal_pinjam, p.status
                    FROM peminjaman p
                    JOIN books b ON p.id_buku = b.id_buku
                    JOIN user  u ON p.id_user = u.id_user
                    ORDER BY p.id_peminjaman DESC LIMIT 8
                """).fetchall(),
                "distribusi_kategori": conn.execute("""
                    SELECT kategori, COUNT(*) as cnt
                    FROM books GROUP BY kategori ORDER BY cnt DESC
                """).fetchall(),
            }


    def get_user_peminjaman(self, id_user: int, search: str = "",
                            status: str = "Semua"):
        """Data peminjaman milik satu anggota/peminjam."""
        self.update_status_terlambat()
        q = """
            SELECT p.id_peminjaman,
                    b.judul, b.penulis, b.penerbit, b.kategori, b.image_path,
                    p.tanggal_pinjam, p.tanggal_kembali,
                    p.tanggal_kembali_aktual,
                    p.status, CAST(p.denda AS INTEGER) AS denda
            FROM peminjaman p
            JOIN books b ON p.id_buku = b.id_buku
            WHERE p.id_user = ?
                AND (b.judul LIKE ? OR b.penulis LIKE ?)
        """
        params = [id_user, f"%{search}%", f"%{search}%"]
        if status == "Aktif":
            q += " AND p.status IN ('Dipinjam','Terlambat','Konfirmasi','Menunggu Persetujuan')"
        elif status == "Pinjaman Saya":
            q += " AND p.status <> 'Dikembalikan'"
        elif status == "Riwayat":
            q += " AND p.status = 'Dikembalikan'"
        elif status != "Semua":
            q += " AND p.status = ?"
            params.append(status)
        q += " ORDER BY p.tanggal_pinjam DESC"
        with self.get_connection() as conn:
            return conn.execute(q, params).fetchall()

    def get_recommended_books(self, limit: int = 6):
        """Rekomendasi sederhana: satu buku terbaik per kategori.

        Prioritas diambil dari jumlah peminjaman di database lokal. Jika sebuah
        kategori belum pernah dipinjam, buku terbaru/stok tersedia dipakai sebagai
        fallback. Tidak memakai rating eksternal agar project tetap offline.
        """
        self.update_status_terlambat()
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT b.id_buku, b.judul, b.penulis, b.penerbit, b.tahun_terbit,
                       b.kategori, b.stok, b.total_stok, b.image_path, b.deskripsi,
                       COUNT(p.id_peminjaman) AS total_pinjam
                FROM books b
                LEFT JOIN peminjaman p ON p.id_buku = b.id_buku
                WHERE b.stok > 0
                GROUP BY b.id_buku
                ORDER BY b.kategori ASC, total_pinjam DESC, b.tahun_terbit DESC, b.judul ASC
                """
            ).fetchall()

        rekomendasi = []
        kategori_terpakai = set()
        for row in rows:
            kategori = row["kategori"] or "Umum"
            if kategori not in kategori_terpakai:
                rekomendasi.append(row)
                kategori_terpakai.add(kategori)
            if len(rekomendasi) >= limit:
                return rekomendasi

        # Jika jumlah kategori sedikit, isi sisanya dengan buku terbaik lain.
        id_terpakai = {r["id_buku"] for r in rekomendasi}
        for row in rows:
            if row["id_buku"] not in id_terpakai:
                rekomendasi.append(row)
            if len(rekomendasi) >= limit:
                break
        return rekomendasi

    def get_member_stats(self, id_user: int) -> dict:
        """Ringkasan personal untuk dashboard anggota/peminjam."""
        self.update_status_terlambat()
        with self.get_connection() as conn:
            return {
                "dipinjam": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman "
                    "WHERE id_user=? AND status IN ('Dipinjam','Terlambat','Konfirmasi')",
                    (id_user,)
                ).fetchone()[0],
                "terlambat": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman "
                    "WHERE id_user=? AND status='Terlambat'",
                    (id_user,)
                ).fetchone()[0],
                "riwayat": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman WHERE id_user=? AND status='Dikembalikan'",
                    (id_user,)
                ).fetchone()[0],
                "tersedia": conn.execute(
                    "SELECT COUNT(*) FROM books WHERE stok > 0"
                ).fetchone()[0],
            }

    # EXPORT DATA

    def get_peminjaman_export(self, status: str = "Semua"):
        self.update_status_terlambat()
        q = """
            SELECT p.id_peminjaman, b.judul, b.penulis,
                    u.nama_lengkap, u.username,
                    p.tanggal_pinjam, p.tanggal_kembali,
                    p.tanggal_kembali_aktual, p.status,
                    CAST(p.denda AS INTEGER) as denda
            FROM peminjaman p
            JOIN books b ON p.id_buku = b.id_buku
            JOIN user  u ON p.id_user = u.id_user
        """
        params = []
        if status == "Aktif":
            q += " WHERE p.status IN ('Dipinjam','Terlambat','Konfirmasi','Menunggu Persetujuan')"
        elif status == "Riwayat":
            q += " WHERE p.status = 'Dikembalikan'"
        elif status != "Semua":
            q += " WHERE p.status = ?"
            params.append(status)
        q += " ORDER BY p.tanggal_pinjam DESC"
        with self.get_connection() as conn:
            return conn.execute(q, params).fetchall()

    def get_books_export(self):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT id_buku,judul,penulis,penerbit,tahun_terbit,"
                "kategori,stok,total_stok,deskripsi FROM books ORDER BY judul"
            ).fetchall()
