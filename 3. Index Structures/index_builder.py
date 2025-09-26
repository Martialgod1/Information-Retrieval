from typing import Dict, List, Tuple, Iterable

from vb_codec import vb_encode, vb_decode, gaps_encode, gaps_decode


Posting = Tuple[int, List[int]]  # (doc_id, positions)


class InMemoryIndex:
    def __init__(self):
        self.term_to_postings: Dict[str, List[Posting]] = {}
        self.doc_lengths: Dict[int, int] = {}

    def add_document(self, doc_id: int, text_tokens: List[str]):
        self.doc_lengths[doc_id] = len(text_tokens)
        positions: Dict[str, List[int]] = {}
        for pos, tok in enumerate(text_tokens):
            positions.setdefault(tok, []).append(pos)
        for term, pos_list in positions.items():
            self.term_to_postings.setdefault(term, []).append((doc_id, pos_list))

    def terms(self) -> List[str]:
        return sorted(self.term_to_postings.keys())

    def postings(self, term: str) -> List[Posting]:
        return self.term_to_postings.get(term, [])


class CompressedIndex:
    def __init__(self, raw_index: InMemoryIndex):
        self.term_to_bytes: Dict[str, List[int]] = {}
        self.doc_lengths = dict(raw_index.doc_lengths)
        for term, plist in raw_index.term_to_postings.items():
            doc_ids = [doc_id for doc_id, _ in plist]
            gaps = gaps_encode(sorted(doc_ids))
            payload = vb_encode(gaps)
            self.term_to_bytes[term] = payload

    def decode_postings(self, term: str) -> List[int]:
        encoded = self.term_to_bytes.get(term)
        if not encoded:
            return []
        gaps = vb_decode(encoded)
        return gaps_decode(gaps)


