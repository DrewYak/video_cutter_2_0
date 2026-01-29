from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QProgressBar,
    QCheckBox,
)
from PySide6.QtCore import Qt

from gui.file_table import FileTable
from controller.batch_controller import BatchController
from config.config_manager import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Cutter 2.0")
        self.resize(900, 600)

        # --- config ---
        self.config_manager = ConfigManager()

        # --- controller ---
        self.batch_controller = BatchController()

        # --- central widget ---
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ===== File controls =====
        file_controls = QHBoxLayout()

        self.btn_add_files = QPushButton("Добавить файлы")
        self.btn_start = QPushButton("Запустить")

        file_controls.addWidget(self.btn_add_files)
        file_controls.addStretch()
        file_controls.addWidget(self.btn_start)

        main_layout.addLayout(file_controls)

        # ===== Checkbox: show full paths =====
        self.checkbox_full_paths = QCheckBox("Показывать полный путь к файлам")
        self.checkbox_full_paths.setChecked(False)
        main_layout.addWidget(self.checkbox_full_paths)

        # ===== File table =====
        self.file_table = FileTable(show_full_path=False)
        main_layout.addWidget(self.file_table)

        # ===== Batch status =====
        self.batch_status_label = QLabel("Ожидание запуска")
        self.batch_status_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.batch_status_label)

        # ===== Progress bars =====
        self.audio_progress = QProgressBar()
        self.audio_progress.setFormat("Аудио: %p%")

        self.video_progress = QProgressBar()
        self.video_progress.setFormat("Видео: %p%")

        self.cut_progress = QProgressBar()
        self.cut_progress.setFormat("Нарезка: %p%")

        main_layout.addWidget(self.audio_progress)
        main_layout.addWidget(self.video_progress)
        main_layout.addWidget(self.cut_progress)

        # ===== Connections =====
        self.btn_add_files.clicked.connect(self.on_add_files)
        self.btn_start.clicked.connect(self.on_start)

        self.checkbox_full_paths.stateChanged.connect(
            self.on_toggle_full_paths
        )

    # ------------------------------------------------------------------

    def on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите видеофайлы",
            "",
            "Video files (*.mp4 *.mkv *.mov)"
        )
        if files:
            self.file_table.add_files(files)

    # ------------------------------------------------------------------

    def on_toggle_full_paths(self, state):
        show_full = state == Qt.Checked
        self.file_table.set_show_full_path(show_full)

    # ------------------------------------------------------------------

    def on_start(self):
        files = self.file_table.get_files()
        if not files:
            return

        # сброс прогресса
        self.audio_progress.setValue(0)
        self.video_progress.setValue(0)
        self.cut_progress.setValue(0)

        self.batch_status_label.setText("Подготовка…")

        # запуск batch controller
        self.batch_controller.start(files)

        worker = self.batch_controller.worker
        if worker is None:
            return

        # === connect worker signals ===
        worker.batch_status_changed.connect(self.on_batch_status_changed)
        worker.audio_progress_changed.connect(self.audio_progress.setValue)
        worker.video_progress_changed.connect(self.video_progress.setValue)
        worker.cut_progress_changed.connect(self.cut_progress.setValue)
        worker.finished.connect(self.on_batch_finished)

    # ------------------------------------------------------------------

    def on_batch_status_changed(self, current: int, total: int):
        self.batch_status_label.setText(
            f"Обрабатывается файл {current} из {total}"
        )

    # ------------------------------------------------------------------

    def on_batch_finished(self):
        self.batch_status_label.setText("Готово")
        self.audio_progress.setValue(100)
        self.video_progress.setValue(100)
        self.cut_progress.setValue(100)
