"""
PustakaDesk — ui_login.py
Login window yang lebih proporsional dan bersih untuk core awal project.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt


class LoginWindow(QMainWindow):
    def __init__(self, db, app, load_stylesheet_fn):
        super().__init__()
        self.db = db
        self.app = app
        self.load_stylesheet = load_stylesheet_fn
        self._dark = False

        self.setWindowTitle("PustakaDesk — Login")
        # Ukuran dibuat lebih tinggi supaya form tidak terlihat padat/nabrak,
        # terutama pada Windows display scaling 125%-150%.
        self.setFixedSize(460, 600)
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
        card.setFixedSize(370, 500)
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
        self.le_username.setText("admin")
        self.le_username.setFixedHeight(42)

        lbl_pass = QLabel("Password")
        lbl_pass.setObjectName("form_label")
        self.le_password = QLineEdit()
        self.le_password.setPlaceholderText("Masukkan password")
        self.le_password.setText("admin123")
        self.le_password.setEchoMode(QLineEdit.Password)
        self.le_password.setFixedHeight(42)
        self.le_password.returnPressed.connect(self._on_login)

        self.btn_login = QPushButton("Masuk")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.setFixedHeight(44)
        self.btn_login.clicked.connect(self._on_login)

        self._btn_toggle = QPushButton("🌙  Tema Gelap")
        self._btn_toggle.setObjectName("btn_outline")
        self._btn_toggle.setFixedHeight(38)
        self._btn_toggle.clicked.connect(self._toggle_theme)

        hint = QLabel("Admin: admin/admin123\nPeminjam: budi/budi123")
        hint.setObjectName("login_hint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)

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
        card_layout.addSpacing(24)
        card_layout.addWidget(self.btn_login)
        card_layout.addSpacing(12)
        card_layout.addWidget(self._btn_toggle)
        card_layout.addSpacing(14)
        card_layout.addWidget(hint)
        card_layout.addStretch(1)

        root.addWidget(card, alignment=Qt.AlignCenter)

    def _on_login(self):
        username = self.le_username.text().strip()
        password = self.le_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan password wajib diisi.")
            return

        user = self.db.login(username, password)
        if not user:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah.\n\nCoba: admin/admin123 atau budi/budi123")
            self.le_password.clear()
            self.le_password.setFocus()
            return

        user = dict(user)
        role = str(user.get("role", "")).lower().strip()

        if role in ("admin", "anggota", "peminjam", "member"):
            from ui.ui_main import MainWindow

            self._main = MainWindow(
                self.db,
                user,
                self.app,
                self.load_stylesheet,
                self._dark
            )
            self._main.show()
            self.close()
            return

        QMessageBox.warning(
            self,
            "Login Gagal",
            f"Role pengguna tidak dikenali: {role or '-'}"
        )

    def _toggle_theme(self):
        self._dark = not self._dark
        self.load_stylesheet(self.app, self._dark)
        self._btn_toggle.setText("☀  Tema Terang" if self._dark else "🌙  Tema Gelap")
