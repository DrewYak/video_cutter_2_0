from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QComboBox
)
from PySide6.QtCore import Qt


class EncodingSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        # CRF label
        layout.addWidget(QLabel("CRF:"))

        # CRF slider
        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setRange(0, 51)
        self.crf_slider.setValue(20)
        self.crf_slider.setToolTip(
            "CRF — качество кодирования.\n"
            "Меньше = лучше качество и больший размер файла.\n"
            "Больше = сильнее сжатие и хуже качество.\n"
            "20 — хороший баланс."
        )
        layout.addWidget(self.crf_slider)

        # CRF value label
        self.crf_value_label = QLabel("20")
        self.crf_value_label.setMinimumWidth(30)
        layout.addWidget(self.crf_value_label)

        # Preset
        layout.addWidget(QLabel("Preset:"))

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
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
        self.preset_combo.setCurrentText("veryslow")
        self.preset_combo.setToolTip(
            "Preset — скорость кодирования.\n"
            "Медленнее = лучше сжатие, но дольше обработка."
        )
        layout.addWidget(self.preset_combo)

        layout.addStretch()

        # Signals
        self.crf_slider.valueChanged.connect(self._on_crf_changed)

    def _on_crf_changed(self, value: int):
        self.crf_value_label.setText(str(value))

    def get_values(self) -> dict:
        return {
            "crf": self.crf_slider.value(),
            "preset": self.preset_combo.currentText()
        }

    def set_values(self, crf: int, preset: str):
        self.crf_slider.setValue(crf)
        self.crf_value_label.setText(str(crf))
        self.preset_combo.setCurrentText(preset)
