"""
PustakaDesk — ui_user.py
BELUM DIBUAT (hanya tampil jika role admin)

Isi yang harus dibuat:
- class UserWidget(QWidget)
  - QTableWidget: Nama Lengkap, Username, Role
  - Search + filter role
  - Tombol: Tambah, Edit, Hapus (dengan konfirmasi)
  - Role: 'admin' atau 'anggota'
  - Hapus user tidak boleh jika masih punya pinjaman aktif
"""

import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLineEdit, QComboBox, QPushButton, 
                               QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from logic.logic import UserController

class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data  # Jika ada, berarti mode EDIT
        self.setWindowTitle("Tambah User Baru" if not user_data else "Edit User")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.input_username = QLineEdit()
        self.input_nama = QLineEdit()
        self.input_password = QLineEdit()
        
        if self.user_data:
            self.input_password.setPlaceholderText("Kosongkan jika tidak ingin mengubah")
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            
        self.input_role = QComboBox()
        self.input_role.addItems(["anggota", "admin"])
        
        # Isi data jika dalam mode Edit
        if self.user_data:
            self.input_username.setText(self.user_data["username"])
            # Username 
            self.input_username.setReadOnly(True) 
            self.input_username.setStyleSheet("background-color: #E0E0E0;")
            self.input_nama.setText(self.user_data["nama_lengkap"])
            self.input_role.setCurrentText(self.user_data["role"])
            
        form_layout.addRow("Username *:", self.input_username)
        form_layout.addRow("Nama Lengkap *:", self.input_nama)
        form_layout.addRow("Password *:" if not user_data else "Password Baru:", self.input_password)
        form_layout.addRow("Role:", self.input_role)
        
        layout.addLayout(form_layout)
        
        # Tombol Simpan & Batal
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def validate_and_accept(self):
        """Validasi field sebelum ditutup."""
        if not self.input_username.text().strip() or not self.input_nama.text().strip():
            QMessageBox.warning(self, "Peringatan", "Username dan Nama Lengkap wajib diisi!")
            return
        
        if not self.user_data and not self.input_password.text().strip():
            QMessageBox.warning(self, "Peringatan", "Password wajib diisi untuk user baru!")
            return
            
        self.accept()

    def get_data(self):
        """Mengambil hasil input data."""
        return {
            "username": self.input_username.text().strip(),
            "nama_lengkap": self.input_nama.text().strip(),
            "password": self.input_password.text().strip(),
            "role": self.input_role.currentText()
        }


# Widget Utama Manajemen User
class UserWidget(QWidget):
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db = db_instance  # Instance dari DatabaseBuku
        
        # 1. visual UI
        self.setup_ui()
        
        # 2. Hubungkan ke Controller Logikanya
        self.controller = UserController(self)
        
        # 3. Panggil fungsi muat data lewat jembatan controller (Solusi Eror)
        self.controller.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Cari User:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik username / nama...")
        # Menghubungkan langsung pencarian ke controller
        self.search_input.textChanged.connect(lambda: self.controller.load_data())
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Role:"))
        self.filter_role = QComboBox()
        self.filter_role.addItems(["Semua", "anggota", "admin"])
        self.filter_role.currentTextChanged.connect(lambda: self.controller.load_data())
        filter_layout.addWidget(self.filter_role)
        
        filter_layout.addStretch()
        
        self.btn_tambah = QPushButton("Tambah User")
        self.btn_tambah.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        # Ambil class UserFormDialog langsung dari file ini dan oper ke controller
        self.btn_tambah.clicked.connect(lambda: self.controller.tambah_user_aksi(UserFormDialog))
        
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setStyleSheet("background-color: #2196F3; color: white;")
        self.btn_edit.clicked.connect(lambda: self.controller.edit_user_aksi(UserFormDialog))
        
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setStyleSheet("background-color: #F44336; color: white;")
        self.btn_hapus.clicked.connect(lambda: self.controller.hapus_user_aksi())
        
        filter_layout.addWidget(self.btn_tambah)
        filter_layout.addWidget(self.btn_edit)
        filter_layout.addWidget(self.btn_hapus)
        
        main_layout.addLayout(filter_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nama Lengkap", "Username", "Role"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.table)