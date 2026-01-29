import librosa
import numpy as np


def find_silence_intervals(
    audio_path: str,
    chunk_duration_ms: int,
    silence_threshold_db: float,
    min_silence_duration_ms: int,
    progress_callback=None,
):
    """
    Возвращает список интервалов тишины в миллисекундах:
    [(start_ms, end_ms), ...]
    """

    y, sr = librosa.load(audio_path, sr=None, mono=True)

    chunk_size = int(sr * chunk_duration_ms / 1000)
    total_chunks = int(np.ceil(len(y) / chunk_size))

    silent_chunks = []

    for i in range(total_chunks):
        start = i * chunk_size
        end = min(len(y), start + chunk_size)
        chunk = y[start:end]

        if len(chunk) == 0:
            continue

        rms = np.sqrt(np.mean(chunk ** 2))
        db = 20 * np.log10(rms + 1e-9)

        is_silent = db < silence_threshold_db
        silent_chunks.append(is_silent)

        if progress_callback:
            progress_callback(int((i + 1) / total_chunks * 100))

    # ---- формируем интервалы ----

    intervals = []
    current_start = None

    for i, is_silent in enumerate(silent_chunks):
        if is_silent and current_start is None:
            current_start = i
        elif not is_silent and current_start is not None:
            duration_ms = (i - current_start) * chunk_duration_ms
            if duration_ms >= min_silence_duration_ms:
                intervals.append((
                    current_start * chunk_duration_ms,
                    i * chunk_duration_ms
                ))
            current_start = None

    if current_start is not None:
        duration_ms = (len(silent_chunks) - current_start) * chunk_duration_ms
        if duration_ms >= min_silence_duration_ms:
            intervals.append((
                current_start * chunk_duration_ms,
                len(silent_chunks) * chunk_duration_ms
            ))

    return intervals
