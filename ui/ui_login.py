"""
PustakaDesk — ui_login.py
Tampilan login untuk anggota dan admin.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
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

from ui.auth_widgets import PasswordInput

from utils.session import (
    clear_remembered_user,
    get_remembered_user_id,
    save_remembered_user,
)


class LoginWindow(QMainWindow):
    def __init__(
        self,
        db,
        app,
        load_stylesheet_fn,
        dark: bool = False,
        prefill_username: str = "",
        try_remembered_session: bool = True,
    ):
        super().__init__()
        self.db = db
        self.app = app
        self.load_stylesheet = load_stylesheet_fn
        self._dark = dark
        self._try_remembered_session_enabled = try_remembered_session
        self._opening_main = False

        self.setWindowTitle("PustakaDesk — Login")
        self.setFixedSize(460, 640)

        # QLineEdit.setText hanya menerima string. Nilai selain string dapat
        # muncul bila method navigasi terhubung langsung ke clicked(bool).
        if not isinstance(prefill_username, str):
            prefill_username = ""
        self._build_ui(prefill_username)

        # Dijalankan setelah window selesai dibuat agar perpindahan ke MainWindow
        # tidak mengganggu proses konstruksi tampilan login.
        if self._try_remembered_session_enabled:
            QTimer.singleShot(0, self._try_restore_session)

    def _build_ui(self, prefill_username: str = ""):
        central = QWidget()
        central.setObjectName("login_root")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(22, 22, 22, 22)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedSize(370, 545)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 26, 30, 22)
        card_layout.setSpacing(0)

        logo = QLabel("📚")
        logo.setObjectName("login_icon")
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("PustakaDesk")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Sistem Manajemen Perpustakaan")
        subtitle.setObjectName("login_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("thin_sep")

        lbl_user = QLabel("Username")
        lbl_user.setObjectName("form_label")
        self.le_username = QLineEdit()
        self.le_username.setPlaceholderText("Masukkan username")
        self.le_username.setText(prefill_username)
        self.le_username.setFixedHeight(42)

        lbl_pass = QLabel("Password")
        lbl_pass.setObjectName("form_label")
        self.le_password = PasswordInput("Masukkan password")
        self.le_password.returnPressed.connect(self._on_login)

        self.cb_remember = QCheckBox("Ingat saya di perangkat ini")
        self.cb_remember.setObjectName("remember_me")
        self.cb_remember.setCursor(Qt.PointingHandCursor)

        self.btn_login = QPushButton("Masuk")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.setFixedHeight(44)
        self.btn_login.clicked.connect(lambda _checked=False: self._on_login())

        register_row = QHBoxLayout()
        register_row.setSpacing(4)
        register_row.setAlignment(Qt.AlignCenter)

        register_text = QLabel("Belum punya akun?")
        register_text.setObjectName("auth_switch_text")

        register_link = QPushButton("Daftar sekarang")
        register_link.setObjectName("btn_auth_link")
        register_link.setCursor(Qt.PointingHandCursor)
        register_link.clicked.connect(lambda _checked=False: self._open_register())

        register_row.addWidget(register_text)
        register_row.addWidget(register_link)

        self._btn_toggle = QPushButton("☀  Tema Terang" if self._dark else "🌙  Tema Gelap")
        self._btn_toggle.setObjectName("btn_outline")
        self._btn_toggle.setFixedHeight(38)
        self._btn_toggle.clicked.connect(lambda _checked=False: self._toggle_theme())

        card_layout.addWidget(logo)
        card_layout.addSpacing(8)
        card_layout.addWidget(title)
        card_layout.addSpacing(6)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(16)
        card_layout.addWidget(sep)
        card_layout.addSpacing(20)
        card_layout.addWidget(lbl_user)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.le_username)
        card_layout.addSpacing(16)
        card_layout.addWidget(lbl_pass)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.le_password)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.cb_remember)
        card_layout.addSpacing(18)
        card_layout.addWidget(self.btn_login)
        card_layout.addSpacing(10)
        card_layout.addLayout(register_row)
        card_layout.addSpacing(12)
        card_layout.addWidget(self._btn_toggle)
        card_layout.addStretch(1)

        root.addWidget(card, alignment=Qt.AlignCenter)

        if prefill_username:
            self.le_password.setFocus()
        else:
            self.le_username.setFocus()

    def _on_login(self):
        username = self.le_username.text().strip()
        password = self.le_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan password wajib diisi.")
            return

        user = self.db.login(username, password)
        if not user:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah.")
            self.le_password.clear()
            self.le_password.setFocus()
            return

        user = dict(user)
        if self.cb_remember.isChecked():
            save_remembered_user(int(user["id_user"]))
        else:
            clear_remembered_user()

        self._open_main(user)

    def _try_restore_session(self):
        if self._opening_main:
            return

        user_id = get_remembered_user_id()
        if user_id is None:
            return

        user = self.db.get_user_by_id(user_id)
        if not user:
            clear_remembered_user()
            return

        self._open_main(dict(user))

    def _open_main(self, user: dict):
        if self._opening_main:
            return

        role = str(user.get("role", "")).lower().strip()
        if role not in ("admin", "anggota", "peminjam", "member"):
            clear_remembered_user()
            QMessageBox.warning(
                self,
                "Login Gagal",
                f"Role pengguna tidak dikenali: {role or '-'}",
            )
            return

        self._opening_main = True
        from ui.ui_main import MainWindow

        self._main = MainWindow(
            self.db,
            user,
            self.app,
            self.load_stylesheet,
            self._dark,
        )
        self._main.show()
        self.close()

    def _open_register(self):
        from ui.ui_register import RegisterWindow

        self._register = RegisterWindow(
            self.db,
            self.app,
            self.load_stylesheet,
            dark=self._dark,
        )
        self._register.show()
        self.close()

    def _toggle_theme(self):
        self._dark = not self._dark
        self.load_stylesheet(self.app, self._dark)
        self._btn_toggle.setText("☀  Tema Terang" if self._dark else "🌙  Tema Gelap")
