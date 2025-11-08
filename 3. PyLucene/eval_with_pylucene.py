#!/usr/bin/env python3
"""
PyLucene-based evaluation demo.
Runs queries against an index and computes evaluation metrics.
"""
import argparse
import math
import os
import sys
from typing import Dict, List, Sequence

from lucene import initVM  # type: ignore
from org.apache.lucene.analysis.standard import StandardAnalyzer  # type: ignore
from org.apache.lucene.index import DirectoryReader  # type: ignore
from org.apache.lucene.queryparser.classic import QueryParser  # type: ignore
from org.apache.lucene.search import IndexSearcher  # type: ignore
from org.apache.lucene.search.similarities import (  # type: ignore
    BM25Similarity,
    LMDirichletSimilarity,
    LMJelinekMercerSimilarity,
)
from org.apache.lucene.store import FSDirectory  # type: ignore
from java.nio.file import Paths  # type: ignore


def precision_at_k(rels: Sequence[int], k: int) -> float:
    k = min(k, len(rels))
    if k <= 0:
        return 0.0
    return sum(rels[:k]) / k


def recall_at_k(rels: Sequence[int], k: int, num_relevant_total: int) -> float:
    if num_relevant_total <= 0:
        return 0.0
    return sum(rels[:k]) / num_relevant_total


def average_precision(rels: Sequence[int]) -> float:
    num_rel = 0
    precisions: List[float] = []
    for i, r in enumerate(rels, start=1):
        if r:
            num_rel += 1
            precisions.append(sum(rels[:i]) / i)
    return sum(precisions) / num_rel if num_rel > 0 else 0.0


def dcg_at_k(gains: Sequence[float], k: int) -> float:
    k = min(k, len(gains))
    dcg = 0.0
    for i in range(k):
        dcg += gains[i] / math.log2(i + 2)
    return dcg


def ndcg_at_k(gains: Sequence[float], k: int) -> float:
    ideal = sorted(gains, reverse=True)
    denom = dcg_at_k(ideal, k)
    if denom <= 0:
        return 0.0
    return dcg_at_k(gains, k) / denom


def mrr(list_of_rels: Sequence[Sequence[int]]) -> float:
    if not list_of_rels:
        return 0.0
    rr_sum = 0.0
    for rels in list_of_rels:
        rr = 0.0
        for i, r in enumerate(rels, start=1):
            if r:
                rr = 1.0 / i
                break
        rr_sum += rr
    return rr_sum / len(list_of_rels)


def build_similarity(sim_type: str, mu: float, lam: float):
    sim_type = sim_type.lower()
    if sim_type == "bm25":
        return BM25Similarity()
    elif sim_type in ("dirichlet", "lm-dirichlet"):
        return LMDirichletSimilarity(float(mu))
    elif sim_type in ("jm", "jelinek-mercer"):
        return LMJelinekMercerSimilarity(float(lam))
    else:
        raise ValueError(f"Unknown similarity: {sim_type}. Use 'bm25', 'dirichlet', or 'jm'.")


def evaluate_queries(
    index_path: str,
    queries: List[str],
    relevance: Dict[str, List[int]],
    doc_relevance: Dict[str, int],
    field: str,
    topk: int,
    sim_type: str,
    mu: float,
    lam: float,
):
    initVM()

    directory = FSDirectory.open(Paths.get(index_path))
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)

    similarity = build_similarity(sim_type, mu, lam)
    searcher.setSimilarity(similarity)

    analyzer = StandardAnalyzer()
    parser = QueryParser(field, analyzer)

    all_rels: List[List[int]] = []
    all_gains: List[List[float]] = []

    print(f"Similarity: {sim_type} | field: {field} | topk: {topk}")
    if not relevance and not doc_relevance:
        print("WARNING: No relevance judgments provided. All metrics will be 0.")
        print("Use --relevance to provide judgments by query position, or --doc-relevance by document path.")
    print("=" * 60)

    for qid, query_text in enumerate(queries, start=1):
        try:
            query = parser.parse(query_text)
            hits = searcher.search(query, topk).scoreDocs

            # Get retrieved documents
            stored_fields = reader.storedFields()
            retrieved_docs = []
            for sd in hits:
                doc = stored_fields.document(sd.doc)
                doc_id = doc.get("path") or doc.get("id") or str(sd.doc)
                retrieved_docs.append((doc_id, sd.score))

            # Build relevance list based on retrieved documents
            rels: List[int] = []
            if query_text in relevance:
                # Use positional relevance (by rank)
                rels = relevance[query_text][:topk]
                rels = rels + [0] * (topk - len(rels))  # pad
            elif doc_relevance:
                # Use document-based relevance
                # Match paths flexibly: try full path, path without /app/, and just filename
                for doc_id, _ in retrieved_docs:
                    rel = 0
                    # Try exact match
                    if doc_id in doc_relevance:
                        rel = doc_relevance[doc_id]
                    else:
                        # Try without /app/ prefix
                        doc_id_short = doc_id.replace("/app/", "")
                        if doc_id_short in doc_relevance:
                            rel = doc_relevance[doc_id_short]
                        else:
                            # Try just the filename
                            filename = os.path.basename(doc_id)
                            if filename in doc_relevance:
                                rel = doc_relevance[filename]
                            # Also try with sample_docs/ prefix
                            elif f"sample_docs/{filename}" in doc_relevance:
                                rel = doc_relevance[f"sample_docs/{filename}"]
                    rels.append(rel)
            else:
                # No relevance provided
                rels = [0] * len(retrieved_docs)

            # For nDCG, use relevance as gains (binary or graded)
            gains = [float(r) for r in rels]

            all_rels.append(rels)
            all_gains.append(gains)

            p_at_k = precision_at_k(rels, topk)
            # Calculate total relevant: from positional or sum of doc_relevance
            if query_text in relevance:
                num_rel_total = sum(relevance[query_text])
            elif doc_relevance:
                num_rel_total = sum(1 for v in doc_relevance.values() if v > 0)
            else:
                num_rel_total = 0
            
            r_at_k = recall_at_k(rels, topk, num_rel_total)
            ap = average_precision(rels)
            ndcg = ndcg_at_k(gains, topk)

            print(f"Query {qid}: '{query_text}'")
            print(f"  Retrieved {len(retrieved_docs)} documents:")
            for rank, (doc_id, score) in enumerate(retrieved_docs[:5], 1):  # Show top 5
                rel_label = f"[REL={rels[rank-1]}]" if rank <= len(rels) else ""
                print(f"    {rank}. {doc_id} (score={score:.4f}) {rel_label}")
            if len(retrieved_docs) > 5:
                print(f"    ... and {len(retrieved_docs) - 5} more")
            print(f"  Precision@{topk}: {p_at_k:.4f}")
            print(f"  Recall@{topk}: {r_at_k:.4f} (total relevant: {num_rel_total})")
            print(f"  AP: {ap:.4f}")
            print(f"  nDCG@{topk}: {ndcg:.4f}")
            print()

        except Exception as e:
            print(f"Error processing query '{query_text}': {e}")
            import traceback
            traceback.print_exc()
            all_rels.append([0] * topk)
            all_gains.append([0.0] * topk)

    reader.close()
    directory.close()

    # Aggregate metrics
    map_score = sum(average_precision(rels) for rels in all_rels) / len(all_rels) if all_rels else 0.0
    mrr_score = mrr(all_rels)
    mean_ndcg = sum(ndcg_at_k(gains, topk) for gains in all_gains) / len(all_gains) if all_gains else 0.0

    print("=" * 60)
    print("Aggregate Metrics:")
    print(f"  MAP: {map_score:.4f}")
    print(f"  MRR: {mrr_score:.4f}")
    print(f"  Mean nDCG@{topk}: {mean_ndcg:.4f}")


def main():
    parser = argparse.ArgumentParser(description="PyLucene evaluation demo")
    parser.add_argument("--index", required=True, help="Path to index directory")
    parser.add_argument("--queries", nargs="+", required=True, help="Query strings")
    parser.add_argument(
        "--relevance",
        nargs="+",
        required=False,
        help="Relevance judgments by query position: 'query:rel1,rel2,...' pairs. Example: 'vector space model:1,0,1,0,0' 'query2:0,1,1,0,0'",
    )
    parser.add_argument(
        "--doc-relevance",
        required=False,
        help="Relevance judgments by document path: 'doc_path:rel' pairs (space-separated). Example: 'doc1.txt:1 doc2.txt:0'",
    )
    parser.add_argument("--field", default="contents", help="Field to search")
    parser.add_argument("--topk", type=int, default=10, help="Top-k results")
    parser.add_argument("--similarity", default="bm25", help="Similarity: bm25 | dirichlet | jm")
    parser.add_argument("--mu", type=float, default=2000.0, help="Dirichlet mu")
    parser.add_argument("--lambda", dest="lam", type=float, default=0.2, help="JM lambda")

    args = parser.parse_args()

    # Parse relevance judgments by query position
    relevance: Dict[str, List[int]] = {}
    if args.relevance:
        for pair in args.relevance:
            if ":" in pair:
                q, rels_str = pair.split(":", 1)
                relevance[q] = [int(x) for x in rels_str.split(",")]

    # Parse relevance judgments by document path
    doc_relevance: Dict[str, int] = {}
    if args.doc_relevance:
        for pair in args.doc_relevance.split():
            if ":" in pair:
                doc_path, rel_str = pair.split(":", 1)
                doc_relevance[doc_path] = int(rel_str)

    evaluate_queries(
        index_path=args.index,
        queries=args.queries,
        relevance=relevance,
        doc_relevance=doc_relevance,
        field=args.field,
        topk=args.topk,
        sim_type=args.similarity,
        mu=args.mu,
        lam=args.lam,
    )


if __name__ == "__main__":
    main()

