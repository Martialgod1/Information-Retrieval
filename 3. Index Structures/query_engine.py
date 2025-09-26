from typing import Iterable, List


def intersect_sorted(a: List[int], b: List[int]) -> List[int]:
    i = j = 0
    out: List[int] = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def union_sorted(a: List[int], b: List[int]) -> List[int]:
    i = j = 0
    out: List[int] = []
    while i < len(a) or j < len(b):
        va = a[i] if i < len(a) else None
        vb = b[j] if j < len(b) else None
        if vb is None or (va is not None and va < vb):
            out.append(va)
            i += 1
        elif va is None or vb < va:
            out.append(vb)
            j += 1
        else:  # equal
            out.append(va)
            i += 1
            j += 1
    return out


