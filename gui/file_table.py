import os
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt


class FileTable(QTableWidget):
    COLUMN_NAME = 0
    COLUMN_STATUS = 1
    COLUMN_CUT_TIME = 2

    def __init__(self, parent=None, show_full_path: bool = False):
        super().__init__(parent)

        self._show_full_paths = show_full_path

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels([
            "Файл",
            "Статус",
            "Вырезано"
        ])

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    # ---------- API ----------

    def add_files(self, file_paths: list[str]):
        for path in file_paths:
            self.add_file(path)

    def get_files(self) -> list[str]:
        files = []
        for row in range(self.rowCount()):
            item = self.item(row, self.COLUMN_NAME)
            if item:
                files.append(item.data(Qt.UserRole))
        return files

    def update_cut_time(self, file_path: str, total_silence_ms: int):
        """Обновляет колонку 'Вырезано' для файла"""
        for row in range(self.rowCount()):
            item = self.item(row, self.COLUMN_NAME)
            if item and item.data(Qt.UserRole) == file_path:
                seconds = total_silence_ms // 1000
                minutes = seconds // 60
                seconds = seconds % 60
                text = f"{minutes:02d}:{seconds:02d}"
                self.setItem(
                    row,
                    self.COLUMN_CUT_TIME,
                    QTableWidgetItem(text)
                )
                break

    # ---------- internals ----------

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

    def set_show_full_path(self, show: bool):
        self._show_full_paths = show

        for row in range(self.rowCount()):
            item = self.item(row, self.COLUMN_NAME)
            full_path = item.data(Qt.UserRole)

            item.setText(
                full_path if show else os.path.basename(full_path)
            )
