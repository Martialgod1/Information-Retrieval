from typing import Dict, List, Set


class BooleanIndex:
    def __init__(self, term_to_docs: Dict[str, List[int]]):
        self.term_to_docs = {t: sorted(set(docs)) for t, docs in term_to_docs.items()}

    def docs(self, term: str) -> List[int]:
        return self.term_to_docs.get(term, [])

    @staticmethod
    def intersect(a: List[int], b: List[int]) -> List[int]:
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

    @staticmethod
    def union(a: List[int], b: List[int]) -> List[int]:
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
            else:
                out.append(va)
                i += 1
                j += 1
        return out

    @staticmethod
    def difference(a: List[int], b: List[int]) -> List[int]:
        b_set: Set[int] = set(b)
        return [x for x in a if x not in b_set]


