from typing import Dict, List, Tuple

from weighting import bm25_score, term_frequency, inverse_document_frequency
from vsm import cosine_similarity


def rank_cosine(query_bow: Dict[int, int], docs_tfidf: List[Dict[int, float]], idf: List[float]) -> List[Tuple[int, float]]:
    # Build query tf-idf
    q_vec: Dict[int, float] = {i: term_frequency(tf) * idf[i] for i, tf in query_bow.items()}
    scores: List[Tuple[int, float]] = []
    for doc_id, dvec in enumerate(docs_tfidf):
        scores.append((doc_id, cosine_similarity(q_vec, dvec)))
    return sorted(scores, key=lambda x: x[1], reverse=True)


def rank_bm25(
    query_terms: List[int],
    postings: Dict[int, List[Tuple[int, int]]],  # term_id -> [(doc_id, tf)]
    doc_lengths: List[int],
    avg_dl: float,
    df: List[int],
) -> List[Tuple[int, float]]:
    num_docs = len(doc_lengths)
    scores: Dict[int, float] = {}
    for t in query_terms:
        for doc_id, tf in postings.get(t, []):
            s = bm25_score(tf, doc_lengths[doc_id], avg_dl, df[t], num_docs)
            scores[doc_id] = scores.get(doc_id, 0.0) + s
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


