from typing import Dict, List, Tuple

from boolean_model import BooleanIndex
from weighting import term_frequency, inverse_document_frequency
from vsm import build_tf_idf_vectors, cosine_similarity
from ranked import rank_cosine, rank_bm25


def tokenize_simple(text: str) -> List[str]:
    return [t for t in ''.join(c.lower() if c.isalnum() else ' ' for c in text).split() if t]


def build_corpus() -> Dict[int, str]:
    return {
        0: "cats chase mice dogs chase cats",
        1: "mice are small animals a cat hunts mice",
        2: "birds fly some dogs watch birds",
        3: "cats and dogs are popular pets",
    }


def build_bow_and_vocab(docs: Dict[int, str]) -> Tuple[List[Dict[int, int]], List[str], List[int]]:
    vocab: Dict[str, int] = {}
    bows: List[Dict[int, int]] = []
    for doc_id in range(len(docs)):
        tokens = tokenize_simple(docs[doc_id])
        bow: Dict[int, int] = {}
        for tok in tokens:
            if tok not in vocab:
                vocab[tok] = len(vocab)
            tid = vocab[tok]
            bow[tid] = bow.get(tid, 0) + 1
        bows.append(bow)
    df = [0] * len(vocab)
    for bow in bows:
        for tid in bow.keys():
            df[tid] += 1
    terms = [None] * len(vocab)
    for t, i in vocab.items():
        terms[i] = t
    return bows, terms, df


def boolean_demo(docs: Dict[int, str]):
    term_to_docs: Dict[str, List[int]] = {}
    for doc_id, text in docs.items():
        for tok in set(tokenize_simple(text)):
            term_to_docs.setdefault(tok, []).append(doc_id)
    bidx = BooleanIndex(term_to_docs)
    cats = bidx.docs("cats")
    dogs = bidx.docs("dogs")
    mice = bidx.docs("mice")
    print("Boolean cats:", cats)
    print("Boolean dogs:", dogs)
    print("Boolean mice:", mice)
    print("cats AND dogs:", BooleanIndex.intersect(cats, dogs))
    print("cats OR mice:", BooleanIndex.union(cats, mice))
    print("cats NOT mice:", BooleanIndex.difference(cats, mice))


def ranked_demo(docs: Dict[int, str]):
    bows, terms, df = build_bow_and_vocab(docs)
    num_docs = len(bows)
    idf = [inverse_document_frequency(num_docs, d) for d in df]
    tfidf_docs = build_tf_idf_vectors(bows, len(terms), df)

    # Query: "cats dogs"
    q_tokens = ["cats", "dogs"]
    q_bow: Dict[int, int] = {}
    for q in q_tokens:
        if q in terms:
            tid = terms.index(q)
            q_bow[tid] = q_bow.get(tid, 0) + 1

    print("\nCosine (TF-IDF) ranking for query 'cats dogs':")
    for doc_id, score in rank_cosine(q_bow, tfidf_docs, idf)[:5]:
        print(doc_id, score)

    # BM25 inputs
    doc_lengths = [sum(b.values()) for b in bows]
    avg_dl = sum(doc_lengths) / len(doc_lengths)
    postings: Dict[int, List[Tuple[int, int]]] = {}
    for doc_id, bow in enumerate(bows):
        for tid, tf in bow.items():
            postings.setdefault(tid, []).append((doc_id, tf))

    print("\nBM25 ranking for query 'cats dogs':")
    query_term_ids = [terms.index(t) for t in q_tokens if t in terms]
    for doc_id, score in rank_bm25(query_term_ids, postings, doc_lengths, avg_dl, df)[:5]:
        print(doc_id, score)


if __name__ == "__main__":
    documents = build_corpus()
    print("=== Boolean Retrieval ===")
    boolean_demo(documents)
    print("\n=== Ranked Retrieval (Cosine + BM25) ===")
    ranked_demo(documents)


