import os
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt


class FileTableWidget(QTableWidget):
    COLUMN_NAME = 0
    COLUMN_STATUS = 1
    COLUMN_CUT_TIME = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        self._show_full_paths = False

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels([
            "Файл",
            "Статус",
            "Вырезано"
        ])

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def add_file(self, file_path: str):
        row = self.rowCount()
        self.insertRow(row)

        display_text = (
            file_path if self._show_full_paths
            else os.path.basename(file_path)
        )

        name_item = QTableWidgetItem(display_text)
        name_item.setData(Qt.UserRole, file_path)

        self.setItem(row, self.COLUMN_NAME, name_item)
        self.setItem(row, self.COLUMN_STATUS, QTableWidgetItem("Ожидание"))
        self.setItem(row, self.COLUMN_CUT_TIME, QTableWidgetItem("—"))

    def remove_selected(self):
        row = self.currentRow()
        if row >= 0:
            self.removeRow(row)

    def set_show_full_paths(self, show: bool):
        self._show_full_paths = show

        for row in range(self.rowCount()):
            item = self.item(row, self.COLUMN_NAME)
            full_path = item.data(Qt.UserRole)

            if show:
                item.setText(full_path)
            else:
                item.setText(os.path.basename(full_path))
