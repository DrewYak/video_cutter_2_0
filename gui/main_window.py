# gui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QCheckBox, QLabel
)
from PySide6.QtCore import Qt

from gui.file_table import FileTableWidget
from gui.encoding_settings import EncodingSettingsWidget
from gui.progress_panel import ProgressPanel
from config.config_manager import load_config, save_config
from controller.batch_controller import BatchController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Cutter 2.0")
        self.setMinimumSize(900, 700)

        self.config = load_config()

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # Чекбокс отображения путей
        self.show_paths_checkbox = QCheckBox("Показывать полный путь к файлам")
        main_layout.addWidget(self.show_paths_checkbox)

        # Таблица файлов
        self.file_table = FileTableWidget()
        main_layout.addWidget(self.file_table)

        # Кодирование
        main_layout.addWidget(QLabel("Кодирование:"))
        self.encoding_settings = EncodingSettingsWidget()
        main_layout.addWidget(self.encoding_settings)

        cutting_cfg = self.config["cutting"]
        self.encoding_settings.set_values(
            crf=cutting_cfg["crf"],
            preset=cutting_cfg["preset"]
        )

        # Панель прогресса
        self.progress_panel = ProgressPanel()
        main_layout.addWidget(self.progress_panel)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить файлы")
        self.remove_button = QPushButton("Удалить выбранный")
        self.start_button = QPushButton("Запустить")

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.start_button)

        main_layout.addLayout(buttons_layout)

        # Контроллер
        self.batch_controller = BatchController()

        # Сигналы GUI
        self.add_button.clicked.connect(self.on_add_files)
        self.remove_button.clicked.connect(self.file_table.remove_selected)
        self.show_paths_checkbox.toggled.connect(
            self.file_table.set_show_full_paths
        )
        self.start_button.clicked.connect(self.on_start_clicked)

        # Сигналы контроллера → GUI
        self.batch_controller.batch_status_changed.connect(
            self.progress_panel.set_batch_status
        )
        self.batch_controller.audio_progress_changed.connect(
            self.progress_panel.set_audio_progress
        )
        self.batch_controller.video_progress_changed.connect(
            self.progress_panel.set_video_progress
        )
        self.batch_controller.cut_progress_changed.connect(
            self.progress_panel.set_cut_progress
        )
        self.batch_controller.finished.connect(
            self.progress_panel.reset
        )

    def on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выбрать видеофайлы",
            "",
            "Video files (*.mp4)"
        )
        for file_path in files:
            self.file_table.add_file(file_path)

    def on_start_clicked(self):
        # Сохраняем параметры кодирования
        encoding = self.encoding_settings.get_values()
        self.config["cutting"]["crf"] = encoding["crf"]
        self.config["cutting"]["preset"] = encoding["preset"]
        save_config(self.config)

        # Собираем файлы ИЗ ТАБЛИЦЫ КОРРЕКТНО
        files = []
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)
            full_path = item.data(Qt.UserRole)
            if full_path:
                files.append(full_path)

        # ⬇️ КЛЮЧЕВОЙ МОМЕНТ
        if not files:
            return

        self.progress_panel.reset()
        self.batch_controller.start(files)
