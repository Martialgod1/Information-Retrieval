import argparse
import math
from collections import defaultdict, Counter

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import LMDirichletSimilarity
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


def analyze_terms(analyzer: StandardAnalyzer, field: str, text: str):
    stream = analyzer.tokenStream(field, text)
    tokens = []
    try:
        stream.reset()
        term_attr = stream.addAttribute(CharTermAttribute.class_)
        while stream.incrementToken():
            tokens.append(term_attr.toString())
        stream.end()
    finally:
        stream.close()
    return tokens


def _get_leaf_term_vector(reader, global_doc_id: int, field: str):
    for leaf in reader.leaves():
        base = leaf.docBase
        if global_doc_id >= base and global_doc_id < base + leaf.reader().maxDoc():
            local_doc = global_doc_id - base
            leaf_reader = leaf.reader()
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


def doc_len_from_tv(reader, doc_id: int, field: str) -> int:
    tv = _get_leaf_term_vector(reader, doc_id, field)
    if tv is None:
        return 0
    te = tv.iterator()
    total = 0
    while True:
        try:
            term = te.next()
        except Exception:
            term = None
        if term is None:
            break
        total += te.totalTermFreq()
    return int(total)


def term_counts_from_tv(reader, doc_id: int, field: str) -> dict:
    tv = _get_leaf_term_vector(reader, doc_id, field)
    if tv is None:
        return {}
    te = tv.iterator()
    counts = {}
    while True:
        try:
            term = te.next()
        except Exception:
            term = None
        if term is None:
            break
        counts[term.utf8ToString()] = te.totalTermFreq()
    return counts


def build_rm3(reader, searcher, analyzer, field, query_text, topk, fb_docs, fb_terms, mu, lambd):
    # Base search with LM Dirichlet
    searcher.setSimilarity(LMDirichletSimilarity(mu))
    qp = QueryParser(field, analyzer)
    base_query = qp.parse(query_text)
    hits = searcher.search(base_query, topk).scoreDocs

    # Vocabulary from feedback docs
    feedback_docs = hits[:fb_docs]
    doc_lens = {}
    doc_term_counts = {}
    collection_len = 0
    collection_term_counts = Counter()
    for sd in feedback_docs:
        dl = doc_len_from_tv(reader, sd.doc, field)
        doc_lens[sd.doc] = max(1, dl)
        tmap = term_counts_from_tv(reader, sd.doc, field)
        doc_term_counts[sd.doc] = tmap
        collection_len += dl
        collection_term_counts.update(tmap)
    collection_len = max(1, collection_len)

    # P(w|C)
    p_wc = defaultdict(float)
    for w, c in collection_term_counts.items():
        p_wc[w] = c / collection_len

    # P(q|d) weights (use doc scores as proxies for P(d|q) after softmax)
    # Alternatively, use scoreDocs scores in exp-softmax for stability
    doc_scores = [sd.score for sd in feedback_docs]
    if not doc_scores:
        print("No feedback docs.")
        return
    max_s = max(doc_scores)
    exp_scores = [math.exp(s - max_s) for s in doc_scores]
    z = sum(exp_scores)
    p_d_q = [e / z for e in exp_scores]

    # RM1: P(w|R) = sum_d P(w|d) P(d|q)
    p_w_R = defaultdict(float)
    vocab = set(collection_term_counts.keys())
    for i, sd in enumerate(feedback_docs):
        d = sd.doc
        dl = doc_lens[d]
        counts = doc_term_counts[d]
        for w in counts.keys():
            # Dirichlet-smoothed P(w|d)
            pw_d = (counts[w] + mu * p_wc.get(w, 0.0)) / (dl + mu)
            p_w_R[w] += pw_d * p_d_q[i]

    # Take top fb_terms
    top_terms = sorted(p_w_R.items(), key=lambda x: x[1], reverse=True)[:fb_terms]

    # RM3: interpolate with original query unigram model
    orig_terms = analyze_terms(analyzer, field, query_text)
    orig_counts = Counter(orig_terms)
    orig_len = max(1, sum(orig_counts.values()))
    p_w_q = {w: c / orig_len for w, c in orig_counts.items()}

    final_weights = defaultdict(float)
    for w, p in top_terms:
        final_weights[w] += (1.0 - lambd) * p
    for w, p in p_w_q.items():
        final_weights[w] += lambd * p

    # Build expanded query
    expansion_terms = sorted(final_weights.items(), key=lambda x: x[1], reverse=True)[:fb_terms]
    expanded_query_text = " ".join(list(orig_counts.keys()) + [w for w, _ in expansion_terms if w not in orig_counts])

    # Rerank with LM
    rerank_query = qp.parse(expanded_query_text)
    reranked = searcher.search(rerank_query, topk).scoreDocs
    stored_fields = reader.storedFields()

    print("Original query:", query_text)
    print("Expanded (RM3) query:", expanded_query_text)
    print("\nTop results after RM3:")
    for i, sd in enumerate(reranked, start=1):
        doc = stored_fields.document(sd.doc)
        print(f"{i}. score={sd.score:.4f} path={doc.get('path')} filename={doc.get('filename')}")


def main():
    parser = argparse.ArgumentParser(description="Relevance Model feedback (RM3-style) with PyLucene")
    parser.add_argument("--index", required=True, help="Index directory path (with term vectors)")
    parser.add_argument("--query", required=True, help="Query string")
    parser.add_argument("--field", default="contents", help="Field to search")
    parser.add_argument("--topk", type=int, default=10, help="Number of results")
    parser.add_argument("--fb-docs", type=int, default=5, help="Feedback documents")
    parser.add_argument("--fb-terms", type=int, default=10, help="Feedback terms in expansion")
    parser.add_argument("--mu", type=float, default=2000.0, help="Dirichlet mu")
    parser.add_argument("--lambda", dest="lambd", type=float, default=0.6, help="Interpolation weight for original query (RM3)")
    args = parser.parse_args()

    ensure_jvm()
    directory = FSDirectory.open(Paths.get(args.index))
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer()

    build_rm3(reader, searcher, analyzer, args.field, args.query, args.topk, args.fb_docs, args.fb_terms, args.mu, args.lambd)

    reader.close()


if __name__ == "__main__":
    main()


