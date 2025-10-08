import argparse

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import BM25Similarity
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


def main():
    parser = argparse.ArgumentParser(description="BM25 ranked retrieval with PyLucene")
    parser.add_argument("--index", required=True, help="Index directory path")
    parser.add_argument("--query", required=True, help="Query string")
    parser.add_argument("--field", default="contents", help="Field to search")
    parser.add_argument("--topk", type=int, default=10, help="Number of results to show")
    parser.add_argument("--k1", type=float, default=1.2, help="BM25 k1 parameter")
    parser.add_argument("--b", type=float, default=0.75, help="BM25 b parameter")
    args = parser.parse_args()

    ensure_jvm()

    directory = FSDirectory.open(Paths.get(args.index))
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)
    searcher.setSimilarity(BM25Similarity(args.k1, args.b))

    analyzer = StandardAnalyzer()
    qp = QueryParser(args.field, analyzer)
    query = qp.parse(args.query)

    hits = searcher.search(query, args.topk).scoreDocs
    stored_fields = reader.storedFields()
    for rank, sd in enumerate(hits, start=1):
        doc = stored_fields.document(sd.doc)
        print(f"{rank}. score={sd.score:.4f} path={doc.get('path')} filename={doc.get('filename')}")

    reader.close()


if __name__ == "__main__":
    main()


