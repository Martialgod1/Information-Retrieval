import argparse
import math
from collections import Counter, defaultdict

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import ClassicSimilarity
from org.apache.lucene.store import FSDirectory


def ensure_jvm():
    try:
        env = lucene.getVMEnv()
        if env is None:
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])
    except Exception:
        try:
            lucene.initVM(vmargs=["-Djava.awt.headless=true"])
        except ValueError:
            pass


def parse_query_terms(analyzer: StandardAnalyzer, field: str, query_text: str) -> Counter:
    # Analyze query text into tokens using the analyzer; ensure proper close
    stream = analyzer.tokenStream(field, query_text)
    terms = []
    try:
        stream.reset()
        term_attr = stream.addAttribute(CharTermAttribute.class_)
        while stream.incrementToken():
            terms.append(term_attr.toString())
        stream.end()
    finally:
        stream.close()
    return Counter(terms)


def _get_leaf_term_vector(reader, global_doc_id: int, field: str):
    for leaf in reader.leaves():
        base = leaf.docBase
        if global_doc_id >= base and global_doc_id < base + leaf.reader().maxDoc():
            local_doc = global_doc_id - base
            leaf_reader = leaf.reader()
            # Try common bindings
            tv = None
            try:
                tv = leaf_reader.getTermVector(local_doc, field)
            except Exception:
                pass
            if tv is None:
                try:
                    tv_fields = getattr(leaf_reader, "getTermVectors", None)
                    if callable(tv_fields):
                        fields = tv_fields(local_doc)
                        if fields is not None:
                            tv = fields.terms(field)
                except Exception:
                    pass
            return tv
    return None


def get_doc_term_weights(reader, doc_id: int, field: str) -> dict:
    """
    Returns TF-IDF-like weights using term vectors:
    weight(t,d) = (1 + log tf) * idf, idf = log(1 + N / df)
    """
    tv_terms = _get_leaf_term_vector(reader, doc_id, field)
    if tv_terms is None:
        return {}
    te = tv_terms.iterator()
    N = reader.numDocs()
    weights = {}
    while True:
        try:
            term = te.next()
        except Exception:
            term = None
        if term is None:
            break
        term_text = term.utf8ToString()
        tf = te.totalTermFreq()
        df = reader.docFreq(Term(field, term_text))
        if tf <= 0 or df <= 0:
            continue
        w = (1.0 + math.log(tf)) * math.log(1.0 + (N / df))
        weights[term_text] = w
    return weights


def rocchio_expand(reader, searcher, analyzer, field, query_text, topk, prf_k, expand_terms, alpha, beta, gamma):
    # Base search with VSM (ClassicSimilarity)
    searcher.setSimilarity(ClassicSimilarity())
    qp = QueryParser(field, analyzer)
    base_query = qp.parse(query_text)
    hits = searcher.search(base_query, topk).scoreDocs
    stored_fields = reader.storedFields()

    # Build initial query vector
    q_vec = parse_query_terms(analyzer, field, query_text)
    q_weights = defaultdict(float)
    for t, c in q_vec.items():
        q_weights[t] += float(c)

    # Relevant (pseudo) and non-relevant sets
    rel_docs = [sd.doc for sd in hits[:prf_k]]
    nrel_docs = [sd.doc for sd in hits[prf_k:topk]]

    # Centroids
    rel_centroid = defaultdict(float)
    for d in rel_docs:
        for t, w in get_doc_term_weights(reader, d, field).items():
            rel_centroid[t] += w
    if rel_docs:
        for t in list(rel_centroid.keys()):
            rel_centroid[t] /= float(len(rel_docs))

    nrel_centroid = defaultdict(float)
    for d in nrel_docs:
        for t, w in get_doc_term_weights(reader, d, field).items():
            nrel_centroid[t] += w
    if nrel_docs:
        for t in list(nrel_centroid.keys()):
            nrel_centroid[t] /= float(len(nrel_docs))

    # Rocchio: q' = alpha*q + beta*rel - gamma*nrel
    new_weights = defaultdict(float)
    for t, w in q_weights.items():
        new_weights[t] += alpha * w
    for t, w in rel_centroid.items():
        new_weights[t] += beta * w
    for t, w in nrel_centroid.items():
        new_weights[t] -= gamma * w

    # Select top expansion terms (excluding original query terms for cleanliness)
    original_terms = set(q_weights.keys())
    candidates = [(t, w) for t, w in new_weights.items() if t not in original_terms]
    candidates.sort(key=lambda x: x[1], reverse=True)
    expansion = [t for t, _ in candidates[:expand_terms]]

    expanded_query_text = " ".join(list(original_terms) + expansion)

    # Re-run search
    rerank_query = qp.parse(expanded_query_text)
    reranked = searcher.search(rerank_query, topk).scoreDocs

    print("Original query:", query_text)
    print("Expanded query:", expanded_query_text)
    print("\nTop results after feedback:")
    for i, sd in enumerate(reranked, start=1):
        doc = stored_fields.document(sd.doc)
        print(f"{i}. score={sd.score:.4f} path={doc.get('path')} filename={doc.get('filename')}")


def main():
    parser = argparse.ArgumentParser(description="Relevance feedback demos (Rocchio, pseudo RF) with PyLucene")
    parser.add_argument("--index", required=True, help="Index directory path (with term vectors)")
    parser.add_argument("--query", required=True, help="Query string")
    parser.add_argument("--field", default="contents", help="Field to search")
    parser.add_argument("--topk", type=int, default=10, help="Number of results")
    parser.add_argument("--method", choices=["rocchio"], default="rocchio", help="Feedback method")
    parser.add_argument("--prf-k", type=int, default=5, help="Top-K docs assumed relevant (pseudo RF)")
    parser.add_argument("--expand-terms", type=int, default=10, help="Number of expansion terms")
    parser.add_argument("--alpha", type=float, default=1.0, help="Rocchio alpha")
    parser.add_argument("--beta", type=float, default=0.75, help="Rocchio beta")
    parser.add_argument("--gamma", type=float, default=0.0, help="Rocchio gamma")
    args = parser.parse_args()

    ensure_jvm()

    directory = FSDirectory.open(Paths.get(args.index))
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer()

    if args.method == "rocchio":
        rocchio_expand(reader, searcher, analyzer, args.field, args.query, args.topk, args.prf_k, args.expand_terms, args.alpha, args.beta, args.gamma)
    else:
        raise ValueError("Unsupported method")

    reader.close()


if __name__ == "__main__":
    main()


