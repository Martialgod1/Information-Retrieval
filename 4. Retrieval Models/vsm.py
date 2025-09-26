from typing import Dict, List, Tuple
import math

from weighting import term_frequency, inverse_document_frequency


def cosine_similarity(vec_a: Dict[int, float], vec_b: Dict[int, float]) -> float:
    dot = sum(vec_a.get(i, 0.0) * w for i, w in vec_b.items())
    na = math.sqrt(sum(w * w for w in vec_a.values()))
    nb = math.sqrt(sum(w * w for w in vec_b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def build_tf_idf_vectors(
    docs_bow: List[Dict[int, int]],
    vocab_size: int,
    doc_freqs: List[int],
) -> List[Dict[int, float]]:
    num_docs = len(docs_bow)
    idf = [inverse_document_frequency(num_docs, df) for df in doc_freqs]
    tfidf_docs: List[Dict[int, float]] = []
    for bow in docs_bow:
        tfidf: Dict[int, float] = {}
        for term_id, count in bow.items():
            tfidf[term_id] = term_frequency(count) * idf[term_id]
        tfidf_docs.append(tfidf)
    return tfidf_docs


