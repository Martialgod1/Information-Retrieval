from typing import Dict, List, Tuple
import math

from representation import Corpus, Document, build_controlled_vocabulary, bag_of_words


def term_document_matrix(corpus: Corpus, use_lucene: bool = True) -> Tuple[List[str], List[str], List[List[int]]]:
    vocab = build_controlled_vocabulary(corpus, use_lucene=use_lucene)
    terms = [None] * len(vocab)
    for t, i in vocab.items():
        terms[i] = t
    docs = [d.doc_id for d in corpus]
    matrix: List[List[int]] = []
    for doc in corpus:
        bow = bag_of_words(doc, vocab, use_lucene=use_lucene)
        row = [0] * len(terms)
        for term_id, count in bow.items():
            row[term_id] = count
        matrix.append(row)
    return terms, docs, matrix

# TF–IDF = (term frequency weight) × (inverse document frequency). Typical IDF gives higher weight to terms that occur in fewer documents.

def tf_idf_matrix(corpus: Corpus, use_lucene: bool = True) -> Tuple[List[str], List[str], List[List[float]]]:
    terms, docs, counts = term_document_matrix(corpus, use_lucene=use_lucene)
    num_docs = len(docs)
    # compute df
    df = [0] * len(terms)
    for row in counts:
        for j, c in enumerate(row):
            if c > 0:
                df[j] += 1
    idf = [math.log((num_docs + 1) / (df_j + 1)) + 1.0 for df_j in df]
    tfidf: List[List[float]] = []
    for row in counts:
        row_sum = sum(row) or 1
        tfidf.append([ (c / row_sum) * idf[j] for j, c in enumerate(row)])
    return terms, docs, tfidf


