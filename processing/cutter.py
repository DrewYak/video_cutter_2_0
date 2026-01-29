# processing/cutter.py

import subprocess
from typing import List, Tuple


def apply_silence_buffer(
    silence_intervals: List[Tuple[int, int]],
    buffer_ms: int,
    total_duration_ms: int
) -> List[Tuple[int, int]]:
    """
    Сужает интервалы тишины, добавляя защитный буфер речи
    слева и справа.
    """
    buffered = []

    for start, end in silence_intervals:
        new_start = start + buffer_ms
        new_end = end - buffer_ms

        if new_start < 0:
            new_start = 0
        if new_end > total_duration_ms:
            new_end = total_duration_ms

        if new_start < new_end:
            buffered.append((new_start, new_end))

    return buffered


def invert_intervals(
    silence_intervals: List[Tuple[int, int]],
    total_duration_ms: int
) -> List[Tuple[int, int]]:
    keep_intervals = []
    prev_end = 0

    for start, end in silence_intervals:
        if start > prev_end:
            keep_intervals.append((prev_end, start))
        prev_end = end

    if prev_end < total_duration_ms:
        keep_intervals.append((prev_end, total_duration_ms))

    return keep_intervals


def cut_video_with_reencoding(
    input_video: str,
    keep_intervals: List[Tuple[int, int]],
    output_video: str,
    crf: int = 20,
    preset: str = "veryfast"
):
    video_filters = []
    audio_filters = []

    for i, (start, end) in enumerate(keep_intervals):
        start_sec = start / 1000
        end_sec = end / 1000

        video_filters.append(
            f"[0:v]trim=start={start_sec}:end={end_sec},setpts=PTS-STARTPTS[v{i}]"
        )
        audio_filters.append(
            f"[0:a]atrim=start={start_sec}:end={end_sec},asetpts=PTS-STARTPTS[a{i}]"
        )

    video_concat = "".join(f"[v{i}]" for i in range(len(video_filters)))
    audio_concat = "".join(f"[a{i}]" for i in range(len(audio_filters)))

    filter_complex = (
        ";".join(video_filters + audio_filters) +
        f";{video_concat}concat=n={len(video_filters)}:v=1:a=0[vout]"
        f";{audio_concat}concat=n={len(audio_filters)}:v=0:a=1[aout]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_video
    ]

    subprocess.run(cmd, check=True)
