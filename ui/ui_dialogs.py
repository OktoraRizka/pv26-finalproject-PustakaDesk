"""
PustakaDesk — ui_dialogs.py
BELUM DIBUAT

Isi yang harus dibuat (semua QDialog):

1. BukuDialog(QDialog)
   - Form: Judul*, Penulis*, Penerbit, Tahun, Kategori*, Stok*
   - Validasi via logic.validasi_form_buku()
   - Digunakan di ui_buku.py (Tambah + Edit)

2. UserDialog(QDialog)
   - Form: Nama Lengkap*, Username*, Password*, Role*
   - Edit mode: password boleh kosong (tidak berubah)
   - Validasi via logic.validasi_form_user()

3. PeminjamanDialog(QDialog)
   - Form: Buku* (QComboBox stok > 0), Anggota* (QComboBox)
   - Tgl Pinjam* (QDateEdit, default hari ini)
   - Tgl Kembali* (QDateEdit, default +7 hari)
   - Info denda: "Rp 1.000/hari keterlambatan"
   - Validasi via logic.validasi_form_peminjaman()

4. KembalikanDialog(QDialog)
   - Tampilkan info: Judul, Peminjam, Tgl Jatuh Tempo
   - Input: Tgl Dikembalikan (QDateEdit)
   - Preview denda otomatis (update saat tanggal berubah)
   - Gunakan logic.hitung_denda() untuk kalkulasi

5. AboutDialog(QDialog)
   - Nama aplikasi, deskripsi singkat
   - Nama + NIM semua anggota kelompok
"""
raise NotImplementedError("ui_dialogs.py belum dibuat")
