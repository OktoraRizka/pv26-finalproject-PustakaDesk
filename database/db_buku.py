"""
PustakaDesk — DatabaseBuku
Core layer: inisialisasi tabel, CRUD User / Books / Peminjaman
"""
import sqlite3
import hashlib
import os
from datetime import date


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
                    role         VARCHAR(50)  NOT NULL DEFAULT 'anggota'
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
                    total_stok   INTEGER      NOT NULL DEFAULT 1
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
            self._seed(conn)

    def _seed(self, conn: sqlite3.Connection):
        if conn.execute("SELECT COUNT(*) FROM user").fetchone()[0] > 0:
            return

        # Default admin
        conn.execute(
            "INSERT INTO user (username, password, nama_lengkap, role) VALUES (?,?,?,?)",
            ("admin", _hash_password("admin123"), "Administrator", "admin")
        )
        # Sample anggota
        sample_users = [
            ("budi",  _hash_password("budi123"),  "Budi Santoso",  "anggota"),
            ("siti",  _hash_password("siti123"),  "Siti Rahayu",   "anggota"),
            ("rizki", _hash_password("rizki123"), "Rizki Pratama", "anggota"),
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
                "SELECT * FROM user WHERE username=? AND password=?",
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
             "FROM user WHERE (username LIKE ? OR nama_lengkap LIKE ?)")
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
                "SELECT * FROM user WHERE id_user=?", (id_user,)
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
                    new_password: str = ""):
        with self.get_connection() as conn:
            if new_password:
                conn.execute(
                    "UPDATE user SET username=?, password=?, nama_lengkap=?, role=? "
                    "WHERE id_user=?",
                    (username, _hash_password(new_password), nama_lengkap, role, id_user)
                )
            else:
                conn.execute(
                    "UPDATE user SET username=?, nama_lengkap=?, role=? WHERE id_user=?",
                    (username, nama_lengkap, role, id_user)
                )

    def delete_user(self, id_user: int):
        with self.get_connection() as conn:
            active = conn.execute(
                "SELECT COUNT(*) FROM peminjaman "
                "WHERE id_user=? AND status IN ('Dipinjam','Terlambat')",
                (id_user,)
            ).fetchone()[0]
            if active > 0:
                raise ValueError("User masih memiliki pinjaman aktif.")
            conn.execute("DELETE FROM user WHERE id_user=?", (id_user,))

    # BOOKS CRUD

    def get_all_books(self, search: str = "", kategori: str = "Semua",
                      sort_col: str = "judul", sort_order: str = "ASC"):
        safe = {"judul", "penulis", "kategori", "tahun_terbit", "stok"}
        if sort_col not in safe:
            sort_col = "judul"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "ASC"

        q = ("SELECT id_buku, judul, penulis, penerbit, tahun_terbit, "
             "kategori, stok, total_stok FROM books "
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
                    tahun_terbit: int, kategori: str, stok: int):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO books (judul,penulis,penerbit,tahun_terbit,kategori,stok,total_stok) "
                "VALUES (?,?,?,?,?,?,?)",
                (judul, penulis, penerbit, tahun_terbit, kategori, stok, stok)
            )

    def update_book(self, id_buku: int, judul: str, penulis: str,
                    penerbit: str, tahun_terbit: int,
                    kategori: str, total_stok: int):
        with self.get_connection() as conn:
            sedang_dipinjam = conn.execute(
                "SELECT COUNT(*) FROM peminjaman "
                "WHERE id_buku=? AND status IN ('Dipinjam','Terlambat')",
                (id_buku,)
            ).fetchone()[0]
            new_stok = max(0, total_stok - sedang_dipinjam)
            conn.execute(
                "UPDATE books SET judul=?,penulis=?,penerbit=?,tahun_terbit=?,"
                "kategori=?,stok=?,total_stok=? WHERE id_buku=?",
                (judul, penulis, penerbit, tahun_terbit,
                    kategori, new_stok, total_stok, id_buku)
            )

    def delete_book(self, id_buku: int):
        with self.get_connection() as conn:
            active = conn.execute(
                "SELECT COUNT(*) FROM peminjaman "
                "WHERE id_buku=? AND status IN ('Dipinjam','Terlambat')",
                (id_buku,)
            ).fetchone()[0]
            if active > 0:
                raise ValueError("Buku masih dipinjam, tidak bisa dihapus.")
            conn.execute("DELETE FROM books WHERE id_buku=?", (id_buku,))

    # PEMINJAMAN CRUD

    def get_all_peminjaman(self, search: str = "", status: str = "Semua",
                        sort_col: str = "tanggal_pinjam", sort_order: str = "DESC"):
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
        if status != "Semua":
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

    def add_peminjaman(self, id_user: int, id_buku: int,
                        tanggal_pinjam: str, tanggal_kembali: str):
        with self.get_connection() as conn:
            buku = conn.execute(
                "SELECT stok, judul FROM books WHERE id_buku=?", (id_buku,)
            ).fetchone()
            if not buku:
                raise ValueError("Buku tidak ditemukan.")
            if buku["stok"] <= 0:
                raise ValueError(f"Stok buku '{buku['judul']}' habis.")

            conn.execute(
                "INSERT INTO peminjaman (id_user,id_buku,tanggal_pinjam,tanggal_kembali) "
                "VALUES (?,?,?,?)",
                (id_user, id_buku, tanggal_pinjam, tanggal_kembali)
            )
            conn.execute(
                "UPDATE books SET stok = stok - 1 WHERE id_buku=?", (id_buku,)
            )

    def kembalikan_buku(self, id_peminjaman: int,
                        tanggal_aktual: str, denda_per_hari: int = 1000):
        """Proses pengembalian + hitung denda otomatis."""
        with self.get_connection() as conn:
            p = conn.execute(
                "SELECT * FROM peminjaman WHERE id_peminjaman=?",
                (id_peminjaman,)
            ).fetchone()
            if not p:
                raise ValueError("Data peminjaman tidak ditemukan.")
            if p["status"] == "Dikembalikan":
                raise ValueError("Buku sudah dikembalikan sebelumnya.")

            due = date.fromisoformat(p["tanggal_kembali"])
            ret = date.fromisoformat(tanggal_aktual)
            hari_terlambat = max(0, (ret - due).days)
            denda = hari_terlambat * denda_per_hari

            conn.execute(
                "UPDATE peminjaman SET tanggal_kembali_aktual=?, "
                "status='Dikembalikan', denda=? WHERE id_peminjaman=?",
                (tanggal_aktual, denda, id_peminjaman)
            )
            conn.execute(
                "UPDATE books SET stok = stok + 1 WHERE id_buku=?",
                (p["id_buku"],)
            )
            return denda

    def update_status_terlambat(self):
        """Dipanggil saat app start — tandai pinjaman yg melewati jatuh tempo."""
        today = date.today().isoformat()
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE peminjaman SET status='Terlambat' "
                "WHERE status='Dipinjam' AND tanggal_kembali < ?",
                (today,)
            )

    # STATS (untuk Dashboard)

    def get_dashboard_stats(self) -> dict:
        with self.get_connection() as conn:
            return {
                "total_buku":     conn.execute("SELECT COUNT(*) FROM books").fetchone()[0],
                "total_anggota":  conn.execute(
                    "SELECT COUNT(*) FROM user WHERE role='anggota'"
                ).fetchone()[0],
                "sedang_dipinjam": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman WHERE status IN ('Dipinjam','Terlambat')"
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
        q = """
            SELECT p.id_peminjaman,
                    b.judul, b.penulis, b.penerbit, b.kategori,
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
            q += " AND p.status IN ('Dipinjam','Terlambat')"
        elif status != "Semua":
            q += " AND p.status = ?"
            params.append(status)
        q += " ORDER BY p.tanggal_pinjam DESC"
        with self.get_connection() as conn:
            return conn.execute(q, params).fetchall()

    def get_member_stats(self, id_user: int) -> dict:
        """Ringkasan personal untuk dashboard anggota/peminjam."""
        with self.get_connection() as conn:
            return {
                "dipinjam": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman "
                    "WHERE id_user=? AND status IN ('Dipinjam','Terlambat')",
                    (id_user,)
                ).fetchone()[0],
                "terlambat": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman "
                    "WHERE id_user=? AND status='Terlambat'",
                    (id_user,)
                ).fetchone()[0],
                "riwayat": conn.execute(
                    "SELECT COUNT(*) FROM peminjaman WHERE id_user=?",
                    (id_user,)
                ).fetchone()[0],
                "tersedia": conn.execute(
                    "SELECT COUNT(*) FROM books WHERE stok > 0"
                ).fetchone()[0],
            }

    # EXPORT DATA

    def get_peminjaman_export(self, status: str = "Semua"):
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
        if status != "Semua":
            q += " WHERE p.status = ?"
            params.append(status)
        q += " ORDER BY p.tanggal_pinjam DESC"
        with self.get_connection() as conn:
            return conn.execute(q, params).fetchall()

    def get_books_export(self):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT id_buku,judul,penulis,penerbit,tahun_terbit,"
                "kategori,stok,total_stok FROM books ORDER BY judul"
            ).fetchall()
