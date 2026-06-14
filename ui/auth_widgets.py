"""
PustakaDesk — auth_widgets.py
Komponen kecil yang dipakai bersama pada halaman autentikasi.
PasswordInput: Kolom input password dengan tombol tampil/sembunyikan.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QWidget,
)


class PasswordInput(QWidget):
    """Kolom password dengan tombol tampil/sembunyikan yang tetap ringkas.

    Password tidak otomatis ditampilkan. Pengguna harus menekan tombol ``Lihat``
    dan dapat menyembunyikannya kembali dengan tombol yang sama.
    """

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("password_input_row")
        # Wrapper harus memiliki tinggi tetap. Tanpa ini, QVBoxLayout pada form
        # registrasi dapat mengecilkannya dan memotong sisi bawah input.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignVCenter)

        self.field = QLineEdit()
        self.field.setObjectName("password_line_edit")
        self.field.setPlaceholderText(placeholder)
        self.field.setEchoMode(QLineEdit.Password)
        self.field.setFixedHeight(42)

        self.toggle_button = QToolButton()
        self.toggle_button.setObjectName("password_toggle")
        self.toggle_button.setText("Lihat")
        self.toggle_button.setToolTip("Tampilkan password")
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(72, 42)
        self.toggle_button.toggled.connect(self._toggle_visibility)

        layout.addWidget(self.field, 1)
        layout.addWidget(self.toggle_button)

    @property
    def returnPressed(self):
        return self.field.returnPressed

    def text(self) -> str:
        return self.field.text()

    def clear(self) -> None:
        self.field.clear()

    def setFocus(self, reason=Qt.OtherFocusReason) -> None:  # noqa: N802 - mengikuti API Qt
        self.field.setFocus(reason)

    def selectAll(self) -> None:  # noqa: N802 - mengikuti API Qt
        self.field.selectAll()

    def _toggle_visibility(self, visible: bool) -> None:
        self.field.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        self.toggle_button.setText("Sembunyi" if visible else "Lihat")
        self.toggle_button.setToolTip(
            "Sembunyikan password" if visible else "Tampilkan password"
        )
