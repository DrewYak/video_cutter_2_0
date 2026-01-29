from PySide6.QtCore import QObject, Signal, QThread

class Worker(QObject):
    batch_status_changed = Signal(int, int)
    audio_progress_changed = Signal(int)
    video_progress_changed = Signal(int)
    cut_progress_changed = Signal(int)
    finished = Signal()

    def __init__(self, files: list[str]):
        super().__init__()
        self.files = files

    def run(self):
        total = len(self.files)

        for idx, file in enumerate(self.files, start=1):
            # отправляем статус
            self.batch_status_changed.emit(idx, total)

            # здесь будет реальный анализ
            # пока просто имитируем прогресс
            for p in range(0, 101, 20):
                self.audio_progress_changed.emit(p)
                self.video_progress_changed.emit(p)
                self.cut_progress_changed.emit(p)

        # всё закончили
        self.finished.emit()
