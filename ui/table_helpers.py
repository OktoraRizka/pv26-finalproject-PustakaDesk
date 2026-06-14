"""
PustakaDesk — ui/table_helpers.py
Helper tampilan tabel PustakaDesk.

"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtWidgets import QStyle
from PySide6.QtCore import Qt


class NoFocusDelegate(QStyledItemDelegate):
    """Delegate tabel tanpa focus rectangle pada cell aktif."""

    def paint(self, painter, option, index):
        clean_option = QStyleOptionViewItem(option)
        clean_option.state &= ~QStyle.State_HasFocus
        super().paint(painter, clean_option, index)


def apply_clean_table_focus(table):
    """Terapkan tampilan tabel tanpa border fokus cell."""
    table.setItemDelegate(NoFocusDelegate(table))
    table.setFocusPolicy(Qt.NoFocus)
    table.viewport().setFocusPolicy(Qt.NoFocus)
