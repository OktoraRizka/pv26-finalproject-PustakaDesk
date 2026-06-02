"""
PustakaDesk — Logic Layer
Business rules: validasi input, kalkulasi denda, aturan peminjaman.

UI TIDAK boleh langsung akses database — semua lewat sini.
"""
import re
from datetime import date, timedelta
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

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


# LOGIC BUKU
class BukuController:
    def __init__(self, ui_widget):
        self.ui = ui_widget       
        self.db = ui_widget.db    

    def load_kategori_filter(self):
        """Logika memuat daftar kategori ke QComboBox filter."""
        try:
            while self.ui.filter_kategori.count() > 1:
                self.ui.filter_kategori.removeItem(1)
                
            kategori_list = self.db.get_kategori_list()
            for kat in kategori_list:
                if isinstance(kat, tuple):
                    self.ui.filter_kategori.addItem(kat[1], kat[0])
                else:
                    self.ui.filter_kategori.addItem(str(kat), str(kat))
        except Exception as e:
            print(f"Gagal memuat kategori di logic: {e}")

    def load_data(self):
        """Logika memproses filter/sort, query DB, dan merender data ke QTableWidget."""
        self.ui.table.setRowCount(0)  # Reset tabel di UI

        # 1. Ambil nilai dari elemen UI
        search_text = self.ui.search_input.text()
        kategori_filter = self.ui.filter_kategori.currentData()
        sort_raw = self.ui.sort_combo.currentData()

        if kategori_filter == "All":
            kategori_filter = "Semua"

        # 2. Parsing parameter sorting
        sort_col = "judul"
        sort_order = "ASC"

        if sort_raw == "judul_asc":
            sort_col = "judul"
            sort_order = "ASC"
        elif sort_raw == "judul_desc":
            sort_col = "judul"
            sort_order = "DESC"
        elif sort_raw == "tahun_desc":
            sort_col = "tahun_terbit"
            sort_order = "DESC"
        elif sort_raw == "stok_asc":
            sort_col = "stok"
            sort_order = "ASC"

        try:
            # 3. Ambil data dari core database
            buku_list = self.db.get_all_books(
                search=search_text, 
                kategori=kategori_filter, 
                sort_col=sort_col, 
                sort_order=sort_order
            )

            # 4. Tampilkan data ke komponen tabel UI
            for row_idx, buku in enumerate(buku_list):
                self.ui.table.insertRow(row_idx)
                
                display_mapped_values = [
                    buku["judul"], buku["penulis"], buku["penerbit"],
                    buku["tahun_terbit"], buku["kategori"], buku["stok"], buku["total_stok"]
                ]
                
                stok_tersedia = int(buku["stok"])

                for col_idx, value in enumerate(display_mapped_values):
                    item = QTableWidgetItem(str(value))
                    
                    # Logika pewarnaan visual jika stok kosong
                    if stok_tersedia == 0:
                        item.setBackground(QColor("#FFE4E1"))  # Soft Pink
                        item.setForeground(QColor("#D8000C"))  # Teks Merah Tua
                        
                    self.ui.table.setItem(row_idx, col_idx, item)
                
                # Sematkan ID asli database di metadata baris
                self.ui.table.item(row_idx, 0).setData(Qt.UserRole, buku["id_buku"])
                
        except Exception as e:
            print(f"Terjadi kesalahan load data di logic: {e}")

    def get_selected_book_id(self):
        """Helper logika untuk mengambil ID Buku yang sedang aktif di-klik."""
        selected_ranges = self.ui.table.selectedRanges()
        if not selected_ranges:
            QMessageBox.warning(self.ui, "Peringatan", "Silakan pilih baris buku terlebih dahulu!")
            return None
        row = selected_ranges[0].topRow()
        return self.ui.table.item(row, 0).data(Qt.UserRole)

    def tambah_buku_aksi(self, dialog_class):
        """Logika memunculkan pop-up dengan menerima class dialog dari UI"""
        try:
            kategori_exist = self.db.get_kategori_list()
        except:
            kategori_exist = []

        # Menggunakan class dialog yang dikirim oleh UI
        dialog = dialog_class(self.ui, kategori_list=kategori_exist)
        
        if dialog.exec() == 1:
            data = dialog.get_data()
            try:
                self.db.add_book(
                    judul=data["judul"], penulis=data["penulis"], penerbit=data["penerbit"],
                    tahun_terbit=data["tahun_terbit"], kategori=data["kategori"], stok=data["stok"]
                )
                QMessageBox.information(self.ui, "Sukses", f"Buku '{data['judul']}' berhasil ditambahkan!")
                
                # Memanggil fungsi-fungsi lokal yang ada di dalam BukuController
                self.load_data()             # Refresh data tabel buku
                self.load_kategori_filter()   # Refresh daftar kategori di combobox filter
                
            except Exception as e:
                QMessageBox.critical(self.ui, "Error Database", f"Gagal menyimpan ke database:\n{e}")

    def handle_hapus(self):
        """Logika hapus buku dengan konfirmasi dialog."""
        book_id = self.get_selected_book_id()
        if book_id is None:
            return

        row = self.ui.table.selectedRanges()[0].topRow()
        judul_buku = self.ui.table.item(row, 0).text()

        confirm = QMessageBox.question(
            self.ui, "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus buku '{judul_buku}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                if self.db.delete_book(book_id):
                    QMessageBox.information(self.ui, "Sukses", "Buku berhasil dihapus.")
                    self.load_data()
                else:
                    QMessageBox.critical(self.ui, "Gagal", "Gagal menghapus data dari database.")
            except Exception as e:
                QMessageBox.critical(self.ui, "Error", f"Terjadi kesalahan: {e}")

    def handle_edit(self):
        """Tempat menaruh logika pengeditan buku nanti"""
        book_id = self.get_selected_book_id()
        if book_id is None:
            return
        # TODO: Implementasi logika edit panggil dialog mode edit disini
        pass
    
# LoGIC UI USER

class UserController:
    def __init__(self, ui_widget):
        self.ui = ui_widget       # Menyimpan referensi ke objek UserWidget
        self.db = ui_widget.db    # Menghubungkan ke core database

    def load_data(self):
        """Mengambil data dari core database dan menampilkannya ke tabel UI."""
        self.ui.table.setRowCount(0)
        
        search_text = self.ui.search_input.text()
        role_filter = self.ui.filter_role.currentText()
        
        try:
            user_list = self.db.get_all_users(search=search_text, role=role_filter)
            
            for row_idx, user in enumerate(user_list):
                self.ui.table.insertRow(row_idx)
                
                item_nama = QTableWidgetItem(user["nama_lengkap"])
                item_username = QTableWidgetItem(user["username"])
                item_role = QTableWidgetItem(user["role"])
                
                if user["role"] == "admin":
                    item_role.setForeground(QColor("#006622"))
                    item_role.setText("★ admin")
                
                self.ui.table.setItem(row_idx, 0, item_nama)
                self.ui.table.setItem(row_idx, 1, item_username)
                self.ui.table.setItem(row_idx, 2, item_role)
                
                # Menyimpan ID User asli di metadata baris komponen tabel UI
                item_nama.setData(Qt.UserRole, user["id_user"])
                
        except Exception as e:
            print(f"Gagal memuat data user di logic: {e}")

    def get_selected_user_id(self):
        """Helper untuk mengambil ID User dari baris tabel yang dipilih."""
        selected_indexes = self.ui.table.selectionModel().selectedRows()
        if not selected_indexes:
            return None
        row = selected_indexes[0].row()
        return self.ui.table.item(row, 0).data(Qt.UserRole)

    def tambah_user_aksi(self, dialog_class):
        """Membuka dialog form tambah user baru."""
        dialog = dialog_class(self.ui)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.add_user(
                    username=data["username"],
                    password=data["password"],
                    nama_lengkap=data["nama_lengkap"],
                    role=data["role"]
                )
                QMessageBox.information(self.ui, "Sukses", f"User '{data['username']}' berhasil ditambahkan.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self.ui, "Error Database", f"Gagal menambah user (kemungkinan username sudah terpakai):\n{e}")

    def edit_user_aksi(self, dialog_class):
        """Membuka dialog form edit data user."""
        id_user = self.get_selected_user_id()
        if id_user is None:
            QMessageBox.warning(self.ui, "Peringatan", "Pilih user di dalam tabel yang ingin diedit terlebih dahulu!")
            return
            
        try:
            user = self.db.get_user_by_id(id_user)
            if not user:
                return
                
            dialog = dialog_class(self.ui, user_data=user)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                
                self.db.update_user(
                    id_user=id_user,
                    username=data["username"],
                    nama_lengkap=data["nama_lengkap"],
                    role=data["role"],
                    new_password=data["password"]
                )
                QMessageBox.information(self.ui, "Sukses", "Data user berhasil diperbarui.")
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self.ui, "Error Database", f"Gagal mengedit data user:\n{e}")

    def _get_row_by_id(self, target_id):
        """Helper internal untuk mendapatkan indeks baris berdasarkan ID metadata."""
        for row in range(self.ui.table.rowCount()):
            if self.ui.table.item(row, 0).data(Qt.UserRole) == target_id:
                return row
        return None

    def sample_helper_get_name(self, row_idx):
         return self.ui.table.item(row_idx, 0).text() if self.ui.table.item(row_idx, 0) else ""

    def hapus_user_aksi(self):
        """Menghapus data user berdasarkan ID dengan proteksi denda/pinjaman aktif."""
        id_user = self.get_selected_user_id()
        if id_user is None:
            QMessageBox.warning(self.ui, "Peringatan", "Pilih user di dalam tabel yang ingin dihapus terlebih dahulu!")
            return
            
        try:
            user = self.db.get_user_by_id(id_user)
            if user and user["username"] == "admin":
                QMessageBox.critical(self.ui, "Akses Ditolak", "Akun master 'admin' bawaan sistem tidak boleh dihapus!")
                return
                
            konfirmasi = QMessageBox.question(
                self.ui, "Konfirmasi Hapus", 
                f"Apakah Anda yakin ingin menghapus user '{user['nama_lengkap']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if konfirmasi == QMessageBox.Yes:
                try:
                    self.db.delete_user(id_user)
                    QMessageBox.information(self.ui, "Sukses", "User berhasil dihapus dari sistem.")
                    self.load_data()
                except ValueError as val_err:
                    QMessageBox.warning(self.ui, "Gagal Menghapus", str(val_err))
                    
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Terjadi kesalahan sistem:\n{e}")
            

# LOGIC UI DASHBOARD

class DashboardController:
    def __init__(self, ui_widget):
        self.ui = ui_widget       
        self.db = ui_widget.db    

    def refresh(self):
        """Mengambil data riil dari core database dan mendistribusikannya ke komponen UI."""
        try:
            stats = self.db.get_dashboard_stats()

            self.ui.update_card_value(self.ui.card_total_buku, stats["total_buku"])
            self.ui.update_card_value(self.ui.card_total_anggota, stats["total_anggota"])
            self.ui.update_card_value(self.ui.card_dipinjam, stats["sedang_dipinjam"])
            self.ui.update_card_value(self.ui.card_terlambat, stats["terlambat"])

            # Update Tabel Aktivitas Terbaru
            self.ui.table_aktivitas.setRowCount(0)
            aktivitas_list = stats["aktivitas_terbaru"]

            for row_idx, log in enumerate(aktivitas_list):
                self.ui.table_aktivitas.insertRow(row_idx)

                item_judul = QTableWidgetItem(log["judul"])
                item_nama = QTableWidgetItem(log["nama_lengkap"])
                item_tgl = QTableWidgetItem(log["tanggal_pinjam"])
                item_status = QTableWidgetItem(log["status"])

                # Pewarnaan teks status transaksi agar interaktif
                status_str = log["status"]
                if status_str == "Dipinjam":
                    item_status.setForeground(QColor("#FB8C00"))       # Oranye
                elif status_str == "Terlambat":
                    item_status.setForeground(QColor("#E53935"))       # Merah
                    item_status.setText("⚠️ Terlambat")
                elif status_str == "Dikembalikan":
                    item_status.setForeground(QColor("#43A047"))       # Hijau

                self.ui.table_aktivitas.setItem(row_idx, 0, item_judul)
                self.ui.table_aktivitas.setItem(row_idx, 1, item_nama)
                self.ui.table_aktivitas.setItem(row_idx, 2, item_tgl)
                self.ui.table_aktivitas.setItem(row_idx, 3, item_status)

            self.ui.subtitle.setText("Data berhasil diperbarui berdasarkan kondisi database terkini.")

        except Exception as e:
            self.ui.subtitle.setText(f"❌ Gagal memuat statistik database: {e}")
            print(f"Error Dashboard: {e}")