"""
PustakaDesk — ui_register.py
Tampilan registrasi anggota PustakaDesk."""
from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from logic.logic import validasi_form_user
from ui.auth_widgets import PasswordInput


class RegisterWindow(QMainWindow):
    """Form pendaftaran akun anggota.

    Role tidak ditampilkan dan selalu disimpan sebagai ``anggota`` agar
    pengguna umum tidak dapat membuat akun admin sendiri.
    """

    def __init__(self, db, app, load_stylesheet_fn, dark: bool = False):
        super().__init__()
        self.db = db
        self.app = app
        self.load_stylesheet = load_stylesheet_fn
        self._dark = dark

        self.setWindowTitle("PustakaDesk — Daftar Akun")
        self.setFixedSize(500, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("login_root")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(22, 22, 22, 22)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedSize(410, 620)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(0)

        icon = QLabel("📚")
        icon.setObjectName("login_icon")
        icon.setAlignment(Qt.AlignCenter)

        title = QLabel("Buat Akun Anggota")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Daftar untuk mencari, meminjam, dan mengelola riwayat buku.")
        subtitle.setObjectName("login_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("thin_sep")

        self.le_name = self._field("Nama lengkap", "Masukkan nama lengkap")
        self.le_username = self._field("Username", "Gunakan huruf, angka, atau underscore")
        self.le_password = self._field("Password", "Minimal 6 karakter", password=True)
        self.le_confirm = self._field("Konfirmasi password", "Ulangi password", password=True)
        self.le_confirm.returnPressed.connect(self._on_register)

        self.btn_register = QPushButton("Daftar")
        self.btn_register.setObjectName("btn_primary")
        self.btn_register.setFixedHeight(44)
        self.btn_register.clicked.connect(lambda _checked=False: self._on_register())

        login_row = QHBoxLayout()
        login_row.setSpacing(4)
        login_row.setAlignment(Qt.AlignCenter)

        login_text = QLabel("Sudah punya akun?")
        login_text.setObjectName("auth_switch_text")

        login_link = QPushButton("Masuk")
        login_link.setObjectName("btn_auth_link")
        login_link.setCursor(Qt.PointingHandCursor)
        # Sinyal clicked membawa nilai bool. Abaikan nilai tersebut agar tidak
        # terbaca sebagai prefill_username saat kembali ke halaman login.
        login_link.clicked.connect(lambda _checked=False: self._open_login())

        login_row.addWidget(login_text)
        login_row.addWidget(login_link)

        theme_btn = QPushButton("☀  Tema Terang" if self._dark else "🌙  Tema Gelap")
        theme_btn.setObjectName("btn_outline")
        theme_btn.setFixedHeight(36)
        theme_btn.clicked.connect(lambda: self._toggle_theme(theme_btn))

        layout.addWidget(icon)
        layout.addSpacing(6)
        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(subtitle)
        layout.addSpacing(14)
        layout.addWidget(separator)
        layout.addSpacing(16)

        for label, field in (
            ("Nama Lengkap", self.le_name),
            ("Username", self.le_username),
            ("Password", self.le_password),
            ("Konfirmasi Password", self.le_confirm),
        ):
            lbl = QLabel(label)
            lbl.setObjectName("form_label")
            layout.addWidget(lbl)
            layout.addSpacing(5)
            layout.addWidget(field)
            layout.addSpacing(10)

        layout.addSpacing(4)
        layout.addWidget(self.btn_register)
        layout.addSpacing(8)
        layout.addLayout(login_row)
        layout.addSpacing(8)
        layout.addWidget(theme_btn)
        layout.addStretch(1)

        root.addWidget(card, alignment=Qt.AlignCenter)

    @staticmethod
    def _field(_label: str, placeholder: str, password: bool = False):
        if password:
            return PasswordInput(placeholder)
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(42)
        return field

    def _on_register(self):
        name = self.le_name.text().strip()
        username = self.le_username.text().strip()
        password = self.le_password.text()
        confirm = self.le_confirm.text()

        errors = validasi_form_user(username, password, name, is_edit=False)
        if password != confirm:
            errors.append("Konfirmasi password tidak sama.")

        if errors:
            QMessageBox.warning(
                self,
                "Pendaftaran Belum Lengkap",
                "Periksa data berikut:\n\n• " + "\n• ".join(errors),
            )
            return

        try:
            self.db.add_user(username, password, name, role="anggota")
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Username Sudah Digunakan",
                "Gunakan username lain lalu coba kembali.",
            )
            self.le_username.setFocus()
            self.le_username.selectAll()
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Pendaftaran Gagal",
                f"Akun belum dapat dibuat.\n\n{exc}",
            )
            return

        QMessageBox.information(
            self,
            "Akun Berhasil Dibuat",
            "Akun anggota sudah dibuat. Silakan masuk menggunakan username dan password tersebut.",
        )
        self._open_login(prefill_username=username)

    def _open_login(self, prefill_username: str = ""):
        from ui.ui_login import LoginWindow

        # Pengaman terhadap sinyal Qt clicked(bool) atau pemanggilan yang tidak
        # sengaja mengirim nilai selain string.
        if not isinstance(prefill_username, str):
            prefill_username = ""

        self._login = LoginWindow(
            self.db,
            self.app,
            self.load_stylesheet,
            dark=self._dark,
            prefill_username=prefill_username,
            try_remembered_session=False,
        )
        self._login.show()
        self.close()

    def _toggle_theme(self, button: QPushButton):
        self._dark = not self._dark
        self.load_stylesheet(self.app, self._dark)
        button.setText("☀  Tema Terang" if self._dark else "🌙  Tema Gelap")
