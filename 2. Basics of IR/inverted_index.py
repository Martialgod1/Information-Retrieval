from typing import Dict, List, Tuple, Iterable

from representation import Document
from text_processing import process_text


Posting = Tuple[str, List[int]]  # (doc_id, positions)


class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, List[Posting]] = {}

    def add_document(self, doc: Document, use_lucene: bool = True):
        tokens = process_text(doc.text, use_lucene=use_lucene)
        positions: Dict[str, List[int]] = {}
        for pos, token in enumerate(tokens):
            positions.setdefault(token, []).append(pos)
        for term, pos_list in positions.items():
            self.index.setdefault(term, []).append((doc.doc_id, pos_list))

    def build(self, documents: Iterable[Document], use_lucene: bool = True):
        for doc in documents:
            self.add_document(doc, use_lucene=use_lucene)

    def postings(self, term: str) -> List[Posting]:
        return self.index.get(term, [])

    def vocabulary(self) -> List[str]:
        return sorted(self.index.keys())


