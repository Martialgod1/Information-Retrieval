#!/usr/bin/env python3
import argparse
import sys

from lucene import initVM  # type: ignore
from org.apache.lucene.analysis.standard import StandardAnalyzer  # type: ignore
from org.apache.lucene.index import DirectoryReader  # type: ignore
from org.apache.lucene.queryparser.classic import QueryParser  # type: ignore
from org.apache.lucene.search import IndexSearcher  # type: ignore
from org.apache.lucene.search.similarities import (  # type: ignore
    LMDirichletSimilarity,
    LMJelinekMercerSimilarity,
)
from org.apache.lucene.store import FSDirectory  # type: ignore
from java.nio.file import Paths  # type: ignore


def build_similarity(variant: str, mu: float, lam: float):
    v = variant.lower()
    if v in ("dirichlet", "diri", "dir", "lm-dirichlet", "lm_dirichlet"):
        return LMDirichletSimilarity(float(mu))
    if v in ("jm", "jelinek", "jelinek-mercer", "lm-jm", "lm_jm"):
        return LMJelinekMercerSimilarity(float(lam))
    raise ValueError(f"Unknown LM variant: {variant}. Use 'dirichlet' or 'jm'.")


def run_search(index_path: str, query_text: str, field: str, topk: int, variant: str, mu: float, lam: float):
    initVM()

    directory = FSDirectory.open(Paths.get(index_path))
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)

    similarity = build_similarity(variant, mu, lam)
    searcher.setSimilarity(similarity)

    analyzer = StandardAnalyzer()
    parser = QueryParser(field, analyzer)
    query = parser.parse(query_text)

    hits = searcher.search(query, topk).scoreDocs

    print(f"Variant: {variant} | field: {field} | topk: {topk}")
    if variant.lower().startswith("dir"):
        print(f"Dirichlet mu = {mu}")
    else:
        print(f"JM lambda = {lam}")
    print("== Results ==")

    stored_fields = reader.storedFields()
    for rank, sd in enumerate(hits, start=1):
        doc = stored_fields.document(sd.doc)
        doc_id = doc.get("path") or doc.get("id") or str(sd.doc)
        print(f"{rank:2d}. score={sd.score:.4f}\t{doc_id}")

    reader.close()
    directory.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="PyLucene LM retrieval (Dirichlet/JM)")
    parser.add_argument("--index", required=True, help="Path to index directory")
    parser.add_argument("--query", required=True, help="Query string")
    parser.add_argument("--field", default="contents", help="Field to search (default: contents)")
    parser.add_argument("--topk", type=int, default=10, help="Number of results to show")
    parser.add_argument("--variant", default="dirichlet", help="LM variant: dirichlet | jm")
    parser.add_argument("--mu", type=float, default=2000.0, help="Dirichlet mu (if variant=dirichlet)")
    parser.add_argument("--lambda", dest="lam", type=float, default=0.2, help="JM lambda in [0,1] (if variant=jm)")

    args = parser.parse_args(argv)

    run_search(
        index_path=args.index,
        query_text=args.query,
        field=args.field,
        topk=args.topk,
        variant=args.variant,
        mu=args.mu,
        lam=args.lam,
    )


if __name__ == "__main__":
    sys.exit(main())

