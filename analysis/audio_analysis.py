# analysis/audio_analysis.py

from typing import List, Tuple
import numpy as np


def split_into_chunks(
    audio: np.ndarray,
    sample_rate: int,
    chunk_duration_ms: int
) -> List[np.ndarray]:
    """
    Разбивает аудиосигнал на крошки фиксированной длительности.
    """
    chunk_size = int(sample_rate * chunk_duration_ms / 1000)
    chunks = []

    for start in range(0, len(audio), chunk_size):
        end = start + chunk_size
        chunk = audio[start:end]

        if len(chunk) == chunk_size:
            chunks.append(chunk)

    return chunks


def compute_rms_db(chunk: np.ndarray) -> float:
    """
    Вычисляет средний уровень громкости крошки в dB.
    """
    rms = np.sqrt(np.mean(chunk ** 2))

    if rms <= 0:
        return -100.0

    return 20 * np.log10(rms)


def find_silence_intervals(
    audio: np.ndarray,
    sample_rate: int,
    chunk_duration_ms: int,
    silence_threshold_db: float,
    min_silence_duration_ms: int
) -> List[Tuple[int, int]]:
    """
    Находит интервалы тишины в аудиосигнале.

    :return: список интервалов (start_ms, end_ms)
    """
    chunks = split_into_chunks(audio, sample_rate, chunk_duration_ms)

    silent_flags = [
        compute_rms_db(chunk) < silence_threshold_db
        for chunk in chunks
    ]

    intervals = []
    current_start = None

    for i, is_silent in enumerate(silent_flags):
        time_ms = i * chunk_duration_ms

        if is_silent:
            if current_start is None:
                current_start = time_ms
        else:
            if current_start is not None:
                duration = time_ms - current_start
                if duration >= min_silence_duration_ms:
                    intervals.append((current_start, time_ms))
                current_start = None

    # Хвост
    if current_start is not None:
        end_time = len(chunks) * chunk_duration_ms
        duration = end_time - current_start
        if duration >= min_silence_duration_ms:
            intervals.append((current_start, end_time))

    return intervals
