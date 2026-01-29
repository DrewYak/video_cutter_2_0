from PySide6.QtCore import QObject, Signal

from analysis.audio_silence import find_silence_intervals


class Worker(QObject):
    batch_status_changed = Signal(int, int)
    audio_progress_changed = Signal(int)
    video_progress_changed = Signal(int)
    cut_progress_changed = Signal(int)

    # НОВЫЙ сигнал:
    # file_path, intervals_count, total_silence_ms
    file_silence_summary = Signal(str, int, int)

    finished = Signal()

    def __init__(self, files: list[str], config: dict):
        super().__init__()
        self.files = files
        self.config = config

    def run(self):
        total = len(self.files)
        audio_cfg = self.config["audio"]

        for index, file_path in enumerate(self.files, start=1):
            self.batch_status_changed.emit(index, total)
            self.audio_progress_changed.emit(0)

            print(f"[AUDIO] Анализ файла: {file_path}")

            intervals = find_silence_intervals(
                audio_path=file_path,
                chunk_duration_ms=audio_cfg["chunk_duration_ms"],
                silence_threshold_db=audio_cfg["silence_threshold_db"],
                min_silence_duration_ms=audio_cfg["min_silence_duration_ms"],
                progress_callback=self.audio_progress_changed.emit,
            )

            total_silence_ms = sum(
                end - start for start, end in intervals
            )

            print(
                f"[AUDIO] Интервалов тишины: {len(intervals)}, "
                f"суммарно: {total_silence_ms / 1000:.1f} сек"
            )

            # эмитим сводку
            self.file_silence_summary.emit(
                file_path,
                len(intervals),
                total_silence_ms
            )

            # пока заглушки
            self.video_progress_changed.emit(100)
            self.cut_progress_changed.emit(100)

        self.finished.emit()
