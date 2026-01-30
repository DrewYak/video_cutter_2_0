# processing/pipeline.py

from media_io.audio_reader import load_audio

from analysis.audio_analysis import find_silence_intervals
from analysis.video_analysis import analyze_video_inactivity

from processing.intervals import intersect_intervals
from processing.cutter import (
    apply_silence_buffer,
    invert_intervals,
    cut_video_with_reencoding
)


def run_pipeline(input_video: str, output_video: str, config: dict):
    """
    Основной сценарий обработки видео.
    Оркестратор, не знает деталей реализации.
    """

    # ---------- AUDIO ANALYSIS ----------
    audio_cfg = config["audio"]

    audio, sample_rate = load_audio(input_video)

    silence_intervals = find_silence_intervals(
        audio=audio,
        sample_rate=sample_rate,
        chunk_duration_ms=audio_cfg["chunk_duration_ms"],
        silence_threshold_db=audio_cfg["silence_threshold_db"],
        min_silence_duration_ms=audio_cfg["min_silence_duration_ms"]
    )

    total_duration_ms = int(len(audio) / sample_rate * 1000)

    buffered_silence_intervals = apply_silence_buffer(
        silence_intervals,
        buffer_ms=config["cutting"]["buffer_ms"],
        total_duration_ms=total_duration_ms
    )

    # ---------- VIDEO ANALYSIS ----------
    video_cfg = config["video"]

    visual_inactive_intervals = analyze_video_inactivity(
        video_path=input_video,
        video_config=video_cfg
    )

    # ---------- MERGE INTERVALS ----------
    passive_intervals = intersect_intervals(
        buffered_silence_intervals,
        visual_inactive_intervals
    )

    keep_intervals = invert_intervals(
        passive_intervals,
        total_duration_ms
    )

    # ---------- CUT VIDEO ----------
    cut_video_with_reencoding(
        input_video=input_video,
        keep_intervals=keep_intervals,
        output_video=output_video,
        crf=config["cutting"]["crf"],
        preset=config["cutting"]["preset"]
    )

    print("\nГОТОВО.")
    print("Итоговое видео:", output_video)
