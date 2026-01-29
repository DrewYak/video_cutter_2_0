from PySide6.QtCore import QObject, Signal


class BatchController(QObject):
    batch_status_changed = Signal(int, int)   # current, total
    audio_progress_changed = Signal(int)
    video_progress_changed = Signal(int)
    cut_progress_changed = Signal(int)
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []
        self._current_index = 0

    def start(self, files: list[str]):
        if not files:
            return

        self._files = files
        self._current_index = 0
        self._process_next_file()

    def _process_next_file(self):
        total = len(self._files)
        current = self._current_index + 1

        self.batch_status_changed.emit(current, total)

        # ⬇️ ВРЕМЕННАЯ симуляция этапов
        self.audio_progress_changed.emit(100)
        self.video_progress_changed.emit(100)
        self.cut_progress_changed.emit(100)

        self._current_index += 1

        if self._current_index < total:
            self._process_next_file()
        else:
            self.finished.emit()
