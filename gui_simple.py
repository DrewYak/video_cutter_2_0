# gui_simple.py

import sys
import json
import os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QSlider,
    QComboBox
)
from PySide6.QtCore import Qt

from processing.pipeline import run_pipeline


CONFIG_PATH = "config/config.json"


class SimpleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Cutter — simple GUI")
        self.resize(400, 300)

        self.input_video = None

        layout = QVBoxLayout(self)

        # --- file selection ---
        self.file_label = QLabel("Файл не выбран")
        layout.addWidget(self.file_label)

        file_btn = QPushButton("Выбрать видео")
        file_btn.clicked.connect(self.select_file)
        layout.addWidget(file_btn)

        # --- CRF slider ---
        self.crf_label = QLabel("CRF: 20")
        layout.addWidget(self.crf_label)

        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setMinimum(0)
        self.crf_slider.setMaximum(40)
        self.crf_slider.setValue(20)
        self.crf_slider.valueChanged.connect(
            lambda v: self.crf_label.setText(f"CRF: {v}")
        )
        layout.addWidget(self.crf_slider)

        # --- preset selector ---
        layout.addWidget(QLabel("Preset"))

        self.preset_box = QComboBox()
        self.preset_box.addItems([
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow"
        ])
        self.preset_box.setCurrentText("veryslow")
        layout.addWidget(self.preset_box)

        # --- start button ---
        start_btn = QPushButton("Запустить")
        start_btn.clicked.connect(self.start_processing)
        layout.addWidget(start_btn)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать видео",
            "",
            "Video files (*.mp4 *.mkv *.avi)"
        )
        if path:
            self.input_video = path
            self.file_label.setText(os.path.basename(path))

    def load_config(self) -> dict:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def start_processing(self):
        if not self.input_video:
            self.file_label.setText("Сначала выберите файл")
            return

        config = self.load_config()

        # override cutting params
        config["cutting"]["crf"] = self.crf_slider.value()
        config["cutting"]["preset"] = self.preset_box.currentText()

        base, ext = os.path.splitext(self.input_video)
        output_video = f"{base}_cut_crf{config['cutting']['crf']}_{config['cutting']['preset']}{ext}"

        run_pipeline(
            input_video=self.input_video,
            output_video=output_video,
            config=config
        )

        self.file_label.setText("Готово")


def main():
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
