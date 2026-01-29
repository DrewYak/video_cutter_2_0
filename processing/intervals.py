# processing/intervals.py

from typing import List, Tuple


def intersect_intervals(
    a: List[Tuple[int, int]],
    b: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    Пересечение двух списков интервалов.
    """
    result = []
    i = j = 0

    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])

        if start < end:
            result.append((start, end))

        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1

    return result
