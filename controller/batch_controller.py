from PySide6.QtCore import QThread
from controller.worker import Worker


class BatchController:
    def __init__(self, config: dict):
        self.config = config
        self.thread = None
        self.worker = None

    def start(self, files: list[str]):
        if not files:
            return

        # создаём поток
        self.thread = QThread()

        # создаём worker
        self.worker = Worker(files, config=self.config)

        # переносим worker в поток
        self.worker.moveToThread(self.thread)

        # запуск worker при старте потока
        self.thread.started.connect(self.worker.run)

        # корректное завершение
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # старт
        self.thread.start()
