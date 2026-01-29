from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar
)


class ProgressPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Индикатор пакета
        self.batch_label = QLabel("Ожидание запуска")
        layout.addWidget(self.batch_label)

        # Прогресс: аудио
        self.audio_label = QLabel("Анализ аудио")
        self.audio_progress = QProgressBar()
        self.audio_progress.setRange(0, 100)

        layout.addWidget(self.audio_label)
        layout.addWidget(self.audio_progress)

        # Прогресс: видео
        self.video_label = QLabel("Анализ видео")
        self.video_progress = QProgressBar()
        self.video_progress.setRange(0, 100)

        layout.addWidget(self.video_label)
        layout.addWidget(self.video_progress)

        # Прогресс: нарезка
        self.cut_label = QLabel("Нарезка и кодирование")
        self.cut_progress = QProgressBar()
        self.cut_progress.setRange(0, 100)

        layout.addWidget(self.cut_label)
        layout.addWidget(self.cut_progress)

    # Методы управления (будут вызываться контроллером)

    def set_batch_status(self, current: int, total: int):
        self.batch_label.setText(
            f"Обрабатывается файл {current} из {total}"
        )

    def set_audio_progress(self, value: int):
        self.audio_progress.setValue(value)

    def set_video_progress(self, value: int):
        self.video_progress.setValue(value)

    def set_cut_progress(self, value: int):
        self.cut_progress.setValue(value)

    def reset(self):
        self.batch_label.setText("Ожидание запуска")
        self.audio_progress.setValue(0)
        self.video_progress.setValue(0)
        self.cut_progress.setValue(0)
