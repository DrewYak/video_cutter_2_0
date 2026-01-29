# io/audio_reader.py

from typing import Tuple
import librosa
import numpy as np


def load_audio(
    video_path: str,
    target_sr: int = 48000
) -> Tuple[np.ndarray, int]:
    """
    Загружает аудиодорожку из видеофайла.

    :param video_path: путь к видеофайлу
    :param target_sr: целевая частота дискретизации
    :return: кортеж (audio_signal, sample_rate)
    """
    audio_signal, sample_rate = librosa.load(
        video_path,
        sr=target_sr,
        mono=True
    )

    return audio_signal, sample_rate
