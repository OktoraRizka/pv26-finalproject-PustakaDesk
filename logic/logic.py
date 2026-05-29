"""
PustakaDesk — Logic Layer
Business rules: validasi input, kalkulasi denda, aturan peminjaman.

UI TIDAK boleh langsung akses database — semua lewat sini.
"""
import re
from datetime import date, timedelta
from typing import Optional


#  Konstanta

DENDA_PER_HARI   = 1_000   # Rp 1.000/hari
MAX_PINJAM       = 3       # maks buku bersamaan per anggota
DURASI_DEFAULT   = 7       # hari — durasi pinjam default


#  Validasi Umum

def validasi_username(username: str) -> Optional[str]:
    """Return pesan error, atau None jika valid."""
    if not username or not username.strip():
        return "Username tidak boleh kosong."
    if len(username.strip()) < 4:
        return "Username minimal 4 karakter."
    if not re.match(r"^[a-zA-Z0-9_]+$", username.strip()):
        return "Username hanya boleh huruf, angka, dan underscore."
    return None


def validasi_password(password: str) -> Optional[str]:
    if not password:
        return "Password tidak boleh kosong."
    if len(password) < 6:
        return "Password minimal 6 karakter."
    return None


def validasi_nama(nama: str) -> Optional[str]:
    if not nama or not nama.strip():
        return "Nama lengkap tidak boleh kosong."
    if len(nama.strip()) < 3:
        return "Nama minimal 3 karakter."
    return None


def validasi_judul(judul: str) -> Optional[str]:
    if not judul or not judul.strip():
        return "Judul buku tidak boleh kosong."
    if len(judul.strip()) < 2:
        return "Judul minimal 2 karakter."
    return None


def validasi_penulis(penulis: str) -> Optional[str]:
    if not penulis or not penulis.strip():
        return "Nama penulis tidak boleh kosong."
    return None


def validasi_tahun(tahun: int) -> Optional[str]:
    current = date.today().year
    if not (1000 <= tahun <= current):
        return f"Tahun terbit harus antara 1000 dan {current}."
    return None


def validasi_stok(stok: int) -> Optional[str]:
    if stok < 1:
        return "Stok minimal 1."
    if stok > 9999:
        return "Stok terlalu besar."
    return None


def validasi_tanggal_pinjam(tgl_pinjam: date, tgl_kembali: date) -> Optional[str]:
    if tgl_kembali <= tgl_pinjam:
        return "Tanggal kembali harus setelah tanggal pinjam."
    maks = tgl_pinjam + timedelta(days=30)
    if tgl_kembali > maks:
        return "Durasi pinjam maksimal 30 hari."
    return None


#  Validasi Form Lengkap 

def validasi_form_user(username: str, password: str,
                        nama_lengkap: str, is_edit: bool = False) -> list[str]:
    errors = []
    e = validasi_nama(nama_lengkap)
    if e:
        errors.append(e)
    e = validasi_username(username)
    if e:
        errors.append(e)
    if not is_edit:
        e = validasi_password(password)
        if e:
            errors.append(e)
    elif password:  # edit: hanya validasi jika diisi
        e = validasi_password(password)
        if e:
            errors.append(e)
    return errors


def validasi_form_buku(judul: str, penulis: str,
                        tahun: int, stok: int) -> list[str]:
    errors = []
    for fn in (validasi_judul(judul),
                validasi_penulis(penulis),
                validasi_tahun(tahun),
                validasi_stok(stok)):
        if fn:
            errors.append(fn)
    return errors


def validasi_form_peminjaman(id_buku: int, id_user: int,
                                tgl_pinjam: date, tgl_kembali: date) -> list[str]:
    errors = []
    if not id_buku:
        errors.append("Buku belum dipilih.")
    if not id_user:
        errors.append("Anggota belum dipilih.")
    e = validasi_tanggal_pinjam(tgl_pinjam, tgl_kembali)
    if e:
        errors.append(e)
    return errors


#  Kalkulasi Denda 

def hitung_denda(tanggal_kembali: date,
                    tanggal_aktual: date,
                    denda_per_hari: int = DENDA_PER_HARI) -> dict:
    """
    Return dict:
        hari_terlambat : int
        denda          : int (Rp)
        terlambat      : bool
    """
    hari = max(0, (tanggal_aktual - tanggal_kembali).days)
    return {
        "hari_terlambat": hari,
        "denda":          hari * denda_per_hari,
        "terlambat":      hari > 0,
    }


def format_rupiah(nominal: int) -> str:
    """Rp 1.000 format."""
    return f"Rp {nominal:,}".replace(",", ".")


#  Helpers Tanggal 

def tanggal_kembali_default(dari: Optional[date] = None,
                            durasi: int = DURASI_DEFAULT) -> date:
    base = dari or date.today()
    return base + timedelta(days=durasi)


def format_tanggal(iso_str: Optional[str]) -> str:
    """'2025-01-15' → '15 Jan 2025'"""
    if not iso_str or iso_str == "-":
        return "-"
    try:
        d = date.fromisoformat(iso_str)
        bulan = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        return f"{d.day:02d} {bulan[d.month]} {d.year}"
    except (ValueError, IndexError):
        return iso_str
