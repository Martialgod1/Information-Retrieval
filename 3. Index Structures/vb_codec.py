from typing import Iterable, List


def vb_encode_number(n: int) -> List[int]:
    if n < 0:
        raise ValueError("vb_encode_number expects non-negative integers")
    bytes_out: List[int] = []
    while True:
        bytes_out.insert(0, n % 128)
        if n < 128:
            break
        n //= 128
    bytes_out[-1] += 128  # set continuation bit in last byte
    return bytes_out


def vb_encode(numbers: Iterable[int]) -> List[int]:
    out: List[int] = []
    for n in numbers:
        out.extend(vb_encode_number(n))
    return out


def vb_decode(stream: Iterable[int]) -> List[int]:
    n = 0
    numbers: List[int] = []
    for b in stream:
        if b < 128:
            n = 128 * n + b
        else:
            n = 128 * n + (b - 128)
            numbers.append(n)
            n = 0
    return numbers


def gaps_encode(sorted_ids: Iterable[int]) -> List[int]:
    prev = 0
    out: List[int] = []
    for doc_id in sorted_ids:
        out.append(doc_id - prev)
        prev = doc_id
    return out


def gaps_decode(gaps: Iterable[int]) -> List[int]:
    acc = 0
    ids: List[int] = []
    for g in gaps:
        acc += g
        ids.append(acc)
    return ids


