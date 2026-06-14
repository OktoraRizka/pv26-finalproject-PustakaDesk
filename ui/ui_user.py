"""
PustakaDesk — ui_user.py
Halaman manajemen user untuk admin: tambah, edit, hapus akun anggota dan admin lain.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QFrame, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt

from logic.logic import UserController
from ui.table_helpers import apply_clean_table_focus


class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Tambah User" if not user_data else "Edit User")
        self.setObjectName("clean_dialog")
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        title = QLabel("Tambah User" if not user_data else "Edit Data User")
        title.setObjectName("dialog_title")
        subtitle = QLabel("Data akun digunakan untuk membedakan akses admin dan anggota.")
        subtitle.setObjectName("dialog_subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("dialog_form_panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("username")
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama lengkap")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Password" if not user_data else "Password baru (opsional)")

        self.input_role = QComboBox()
        self.input_role.addItems(["anggota", "admin"])

        if self.user_data:
            self.input_username.setText(self.user_data["username"])
            self.input_username.setReadOnly(True)
            self.input_username.setToolTip("Username tidak dapat diubah melalui panel admin.")
            self.input_nama.setText(self.user_data["nama_lengkap"])
            self.input_role.setCurrentText(self.user_data["role"])

        form_layout.addRow("Username *", self.input_username)
        form_layout.addRow("Nama Lengkap *", self.input_nama)
        form_layout.addRow("Password *" if not user_data else "Password Baru", self.input_password)
        form_layout.addRow("Role", self.input_role)
        panel_layout.addLayout(form_layout)
        layout.addWidget(panel)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def validate_and_accept(self):
        if not self.input_username.text().strip() or not self.input_nama.text().strip():
            QMessageBox.warning(self, "Peringatan", "Username dan nama lengkap wajib diisi.")
            return
        if not self.user_data and not self.input_password.text().strip():
            QMessageBox.warning(self, "Peringatan", "Password wajib diisi untuk user baru.")
            return
        self.accept()

    def get_data(self):
        return {
            "username": self.input_username.text().strip(),
            "nama_lengkap": self.input_nama.text().strip(),
            "password": self.input_password.text().strip(),
            "role": self.input_role.currentText(),
        }


class UserWidget(QWidget):
    def __init__(self, db_instance, parent=None):
        super().__init__(parent)
        self.db = db_instance
        self.setObjectName("page")
        self.setup_ui()
        self.controller = UserController(self)
        self.controller.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("page_header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(12)

        title = QLabel("Manajemen User")
        title.setObjectName("page_title")
        header_layout.addWidget(title, 1)
        main_layout.addWidget(header)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        filter_layout = QHBoxLayout(toolbar)
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik username / nama...")
        self.search_input.textChanged.connect(lambda: self.controller.load_data())

        self.filter_role = QComboBox()
        self.filter_role.addItems(["Semua", "anggota", "admin"])
        self.filter_role.currentTextChanged.connect(lambda: self.controller.load_data())

        self.btn_tambah = QPushButton("Tambah User")
        self.btn_tambah.setObjectName("btn_success")
        self.btn_tambah.clicked.connect(lambda: self.controller.tambah_user_aksi(UserFormDialog))

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setObjectName("btn_primary")
        self.btn_edit.clicked.connect(lambda: self.controller.edit_user_aksi(UserFormDialog))

        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setObjectName("btn_danger")
        self.btn_hapus.clicked.connect(lambda: self.controller.hapus_user_aksi())

        filter_layout.addWidget(QLabel("Cari"))
        filter_layout.addWidget(self.search_input, 2)
        filter_layout.addWidget(QLabel("Role"))
        filter_layout.addWidget(self.filter_role, 1)
        filter_layout.addStretch()
        filter_layout.addWidget(self.btn_tambah)
        filter_layout.addWidget(self.btn_edit)
        filter_layout.addWidget(self.btn_hapus)
        main_layout.addWidget(toolbar)

        self.table = QTableWidget()
        self.table.setObjectName("data_table")
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nama Lengkap", "Username", "Role"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        apply_clean_table_focus(self.table)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.table, 1)

    def refresh(self):
        if hasattr(self, "controller"):
            self.controller.load_data()
