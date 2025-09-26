from typing import Dict, List
import math


def term_frequency(count: int) -> float:
    # log-normalized TF
    return 1.0 + math.log(count) if count > 0 else 0.0


def inverse_document_frequency(num_docs: int, doc_freq: int) -> float:
    # IDF with +1 smoothing
    return math.log((num_docs + 1) / (doc_freq + 1)) + 1.0


def tf_idf_weight(tf_count: int, num_docs: int, doc_freq: int) -> float:
    return term_frequency(tf_count) * inverse_document_frequency(num_docs, doc_freq)


def bm25_score(tf_count: int, doc_len: int, avg_dl: float, df: int, num_docs: int, k1: float = 1.2, b: float = 0.75) -> float:
    idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1.0)
    denom = tf_count + k1 * (1.0 - b + b * (doc_len / max(avg_dl, 1e-9)))
    tf_sat = (tf_count * (k1 + 1.0)) / max(denom, 1e-9)
    return idf * tf_sat


