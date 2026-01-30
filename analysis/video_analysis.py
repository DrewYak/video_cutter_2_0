# analysis/video_analysis.py

import cv2
import numpy as np
import time

from media_io.video_reader import open_video


def mask_webcam(frame, webcam_area):
    x = webcam_area["x"]
    y = webcam_area["y"]
    w = webcam_area["width"]
    h = webcam_area["height"]
    frame[y:y + h, x:x + w] = 0
    return frame


def preprocess_frame(frame, scale=1.0):
    if scale != 1.0:
        frame = cv2.resize(
            frame,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray


def frame_change_metric(prev_frame, curr_frame, pixel_diff_threshold):
    diff = cv2.absdiff(prev_frame, curr_frame)
    changed_pixels = np.sum(diff > pixel_diff_threshold)
    total_pixels = diff.size
    return changed_pixels / total_pixels


class SlidingActivityWindow:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []

    def update(self, value):
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return sum(self.values)


class VisualInactivityDetector:
    def __init__(self, activity_threshold, min_inactive_duration_ms):
        self.activity_threshold = activity_threshold
        self.min_inactive_duration_ms = min_inactive_duration_ms

        self.inactive_start = None
        self.intervals = []

    def update(self, time_ms, activity_score):
        if activity_score < self.activity_threshold:
            if self.inactive_start is None:
                self.inactive_start = time_ms
        else:
            if self.inactive_start is not None:
                duration = time_ms - self.inactive_start
                if duration >= self.min_inactive_duration_ms:
                    self.intervals.append(
                        (self.inactive_start, time_ms)
                    )
                self.inactive_start = None

    def finalize(self, last_time_ms):
        if self.inactive_start is not None:
            duration = last_time_ms - self.inactive_start
            if duration >= self.min_inactive_duration_ms:
                self.intervals.append(
                    (self.inactive_start, last_time_ms)
                )


def analyze_video_inactivity(video_path: str, video_config: dict):
    """
    Полный автономный анализ видео на визуальную неактивность.
    Чёрный ящик: video_path -> интервалы.
    """

    analysis_cfg = video_config["analysis"]

    cap, fps, frame_count = open_video(video_path)

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

        frame = mask_webcam(frame, video_config["webcam_area"])

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

        now = time.time()
        if now - last_progress_time >= 5:
            percent = frame_index / frame_count * 100
            elapsed = int(now - start_time)
            print(f"Видео-анализ: {percent:.1f}% | {elapsed} сек")
            last_progress_time = now

    cap.release()

    last_time_ms = int(frame_index / fps * 1000)
    detector.finalize(last_time_ms)

    return detector.intervals
