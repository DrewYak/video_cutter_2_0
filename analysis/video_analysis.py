# analysis/video_analysis.py

import cv2
import numpy as np
from typing import Dict, List, Tuple
from collections import deque


def mask_webcam(frame: np.ndarray, webcam_area: Dict) -> np.ndarray:
    x = webcam_area["x"]
    y = webcam_area["y"]
    w = webcam_area["width"]
    h = webcam_area["height"]

    masked = frame.copy()
    masked[y:y+h, x:x+w] = 0
    return masked


def preprocess_frame(
    frame: np.ndarray,
    scale: float
) -> np.ndarray:
    """
    Downscale + grayscale + лёгкое сглаживание.
    """
    if scale != 1.0:
        frame = cv2.resize(
            frame,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    return blurred


def frame_change_metric(
    prev_frame: np.ndarray,
    curr_frame: np.ndarray,
    pixel_diff_threshold: int
) -> float:
    diff = cv2.absdiff(prev_frame, curr_frame)
    changed = diff > pixel_diff_threshold
    return float(np.sum(changed)) / changed.size


class SlidingActivityWindow:
    def __init__(self, window_size: int):
        self.window = deque(maxlen=window_size)

    def update(self, value: float) -> float:
        self.window.append(value)
        return sum(self.window)


class VisualInactivityDetector:
    def __init__(
        self,
        activity_threshold: float,
        min_inactive_duration_ms: int
    ):
        self.activity_threshold = activity_threshold
        self.min_inactive_duration_ms = min_inactive_duration_ms
        self.inactive_start_ms = None
        self.intervals: List[Tuple[int, int]] = []

    def update(self, time_ms: int, activity_score: float):
        is_active = activity_score >= self.activity_threshold

        if not is_active:
            if self.inactive_start_ms is None:
                self.inactive_start_ms = time_ms
        else:
            if self.inactive_start_ms is not None:
                duration = time_ms - self.inactive_start_ms
                if duration >= self.min_inactive_duration_ms:
                    self.intervals.append((self.inactive_start_ms, time_ms))
                self.inactive_start_ms = None

    def finalize(self, last_time_ms: int):
        if self.inactive_start_ms is not None:
            duration = last_time_ms - self.inactive_start_ms
            if duration >= self.min_inactive_duration_ms:
                self.intervals.append((self.inactive_start_ms, last_time_ms))
