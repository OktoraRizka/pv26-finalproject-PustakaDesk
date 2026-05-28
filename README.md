# PustakaDesk 📚

Sistem Manajemen Perpustakaan berbasis **PySide6 + SQLite**  
Tugas Akhir Pemrograman Visual — Semester Genap 2025/2026

---

## Anggota Kelompok

| Nama | NIM | Bagian |
|------|-----|--------|
| [Nama 1] | [NIM 1] | Core: |
| [Nama 2] | [NIM 2] | UI:  |
| [Nama 3] | [NIM 3] | UI:  |

---

## Cara Menjalankan

```bash
# 1. Clone repository
git clone https://github.com/[username]/pv26-finalproject-pustakaDesk.git
cd pv26-finalproject-pustakaDesk

# 2. Install dependensi
pip install -r requirements.txt

# 3. Jalankan aplikasi
python main.py
```

**Akun default:**  
- Username: `admin` | Password: `admin123` (role: admin)  
- Username: `budi`  | Password: `budi123`  (role: anggota)

---

## Fitur

-  Login + manajemen sesi (role: admin / anggota)
-  Role-based interface: admin memakai UI operasional, anggota memakai portal katalog
-  Katalog buku (CRUD + search + filter kategori + sort)
-  Manajemen anggota (khusus admin)
-  Peminjaman & pengembalian buku
-   Kalkulasi denda otomatis (Rp 1.000/hari terlambat)
-  Dashboard ringkasan + chart distribusi kategori
-  Ekspor laporan ke CSV dan PDF
-  Tema gelap / terang

---

## Screenshot

> *( screenshot setelah UI selesai)*

---

## Struktur Project

```
PustakaDesk/
├── database/       → db_buku.py (SQLite CRUD)
├── logic/          → logic.py (validasi, kalkulasi)
├── style/          → style.qss / style_dark.qss
├── ui/             → semua halaman UI
│   └── ui_member.py → halaman khusus anggota/peminjam
├── utils/          → export CSV + PDF
└── main.py         → entry point
```
