# main.py

from media_io.audio_reader import load_audio
from media_io.video_reader import open_video

from analysis.audio_analysis import find_silence_intervals
from analysis.video_analysis import (
    mask_webcam,
    preprocess_frame,
    frame_change_metric,
    SlidingActivityWindow,
    VisualInactivityDetector
)

from processing.intervals import intersect_intervals
from processing.cutter import (
    apply_silence_buffer,
    invert_intervals,
    cut_video_with_reencoding
)

import json
import time


def main():
    input_video = "06.01_crf20_veryslow.mp4"
    output_video = "final_output_2.mp4"

    # ---------- CONFIG ----------
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

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
    analysis_cfg = video_cfg["analysis"]

    cap, fps, frame_count = open_video(input_video)

    activity_window = SlidingActivityWindow(
        window_size=analysis_cfg["activity_window_frames"]
    )

    detector = VisualInactivityDetector(
        activity_threshold=analysis_cfg["activity_threshold"],
        min_inactive_duration_ms=analysis_cfg["min_inactive_duration_ms"]
    )

    prev_processed = None
    frame_index = 0

    last_progress_time = time.time()
    start_time = last_progress_time

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # маска вебкамеры
        frame = mask_webcam(frame, video_cfg["webcam_area"])

        # downscale + preprocess
        processed = preprocess_frame(
            frame,
            scale=analysis_cfg["analysis_scale"]
        )

        if prev_processed is not None:
            change = frame_change_metric(
                prev_processed,
                processed,
                pixel_diff_threshold=analysis_cfg["pixel_diff_threshold"]
            )

            activity_score = activity_window.update(change)

            time_ms = int(frame_index / fps * 1000)
            detector.update(time_ms, activity_score)

        prev_processed = processed
        frame_index += 1

        # прогресс раз в ~5 секунд
        now = time.time()
        if now - last_progress_time >= 5:
            percent = frame_index / frame_count * 100
            elapsed = int(now - start_time)
            print(f"Видео-анализ: {percent:.1f}% | {elapsed} сек")
            last_progress_time = now

    cap.release()

    last_time_ms = int(frame_index / fps * 1000)
    detector.finalize(last_time_ms)

    visual_inactive_intervals = detector.intervals

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


if __name__ == "__main__":
    main()
