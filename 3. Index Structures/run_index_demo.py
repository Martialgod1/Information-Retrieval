from typing import List

from vb_codec import vb_encode, vb_decode, gaps_encode, gaps_decode
from index_builder import InMemoryIndex, CompressedIndex
from query_engine import intersect_sorted, union_sorted


def tokenize_simple(text: str) -> List[str]:
    return [t for t in ''.join(c.lower() if c.isalnum() else ' ' for c in text).split() if t]


def build_sample_index() -> InMemoryIndex:
    docs = {
        1: "cats chase mice dogs chase cats",
        2: "mice are small animals a cat hunts mice",
        3: "birds fly some dogs watch birds",
    }
    idx = InMemoryIndex()
    for doc_id, text in docs.items():
        idx.add_document(doc_id, tokenize_simple(text))
    return idx


def demo_creation_and_compression():
    print("=== Index creation ===")
    raw = build_sample_index()
    print("terms:", raw.terms())
    print("postings('dogs'):", raw.postings("dogs"))

    print("\n=== Index compression (gaps + VB) ===")
    comp = CompressedIndex(raw)
    print("encoded bytes for 'dogs':", comp.term_to_bytes.get("dogs"))
    print("decoded postings for 'dogs':", comp.decode_postings("dogs"))


def demo_queries():
    print("\n=== Query execution ===")
    raw = build_sample_index()
    # Build doc-id lists per term
    def docids(term: str) -> List[int]:
        return sorted(doc_id for doc_id, _ in raw.postings(term))

    dogs = docids("dogs")
    cats = docids("cats")
    mice = docids("mice")
    print("dogs:", dogs)
    print("cats:", cats)
    print("mice:", mice)

    print("AND(dogs, cats):", intersect_sorted(dogs, cats))
    print("OR(cats, mice):", union_sorted(cats, mice))


if __name__ == "__main__":
    demo_creation_and_compression()
    demo_queries()


