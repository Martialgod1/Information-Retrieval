from dataclasses import dataclass
from typing import Dict, List, Iterable

from text_processing import process_text


@dataclass
class Document:
    doc_id: str
    title: str
    text: str

    def tokens(self, use_lucene: bool = True) -> List[str]:
        return process_text(self.text, use_lucene=use_lucene)


class Corpus:
    def __init__(self, documents: Iterable[Document]):
        self.documents: List[Document] = list(documents)

    def __iter__(self):
        return iter(self.documents)

    def __len__(self) -> int:
        return len(self.documents)

    def all_tokens(self, use_lucene: bool = True) -> Iterable[str]:
        for doc in self.documents:
            for tok in doc.tokens(use_lucene=use_lucene):
                yield tok


def build_controlled_vocabulary(corpus: Corpus, min_freq: int = 1, use_lucene: bool = True) -> Dict[str, int]:
    term_to_id: Dict[str, int] = {}
    term_freq: Dict[str, int] = {}
    for tok in corpus.all_tokens(use_lucene=use_lucene):
        term_freq[tok] = term_freq.get(tok, 0) + 1
    for term, freq in sorted(term_freq.items()):
        if freq >= min_freq:
            term_to_id[term] = len(term_to_id)
    return term_to_id


def bag_of_words(doc: Document, vocabulary: Dict[str, int], use_lucene: bool = True) -> Dict[int, int]:
    bow: Dict[int, int] = {}
    for tok in doc.tokens(use_lucene=use_lucene):
        if tok in vocabulary:
            term_id = vocabulary[tok]
            bow[term_id] = bow.get(term_id, 0) + 1
    return bow


