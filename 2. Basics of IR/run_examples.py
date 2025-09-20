from typing import List

from representation import Document, Corpus, build_controlled_vocabulary, bag_of_words
from inverted_index import InvertedIndex
from matrix import term_document_matrix, tf_idf_matrix
from text_processing import process_text


def sample_corpus() -> Corpus:
    docs: List[Document] = [
        Document(doc_id="D1", title="Cats and Dogs", text="Cats chase mice. Dogs chase cats!"),
        Document(doc_id="D2", title="About Mice", text="Mice are small animals. A cat hunts mice."),
        Document(doc_id="D3", title="Birds", text="Birds fly. Some dogs watch birds."),
    ]
    return Corpus(docs)


def demonstrate_text_processing():
    text = "Dogs, dogs! are running and chased the CATS."
    print("\n=== Text processing ===")
    print("input:", text)
    print("tokens:", process_text(text, use_lucene=True))
    print("tokens (no lucene):", process_text(text, use_lucene=False))


def demonstrate_document_representation(corpus: Corpus):
    print("\n=== Document representation ===")
    for d in corpus:
        print(d.doc_id, d.title, "->", d.tokens(use_lucene=True))


def demonstrate_controlled_vocabulary(corpus: Corpus):
    print("\n=== Controlled vocabulary ===")
    vocab = build_controlled_vocabulary(corpus, min_freq=1, use_lucene=True)
    print("size:", len(vocab))
    print("sample terms:", sorted(list(vocab.keys()))[:15])
    return vocab


def demonstrate_free_text_representation(corpus: Corpus, vocab):
    print("\n=== Free text representation (bag-of-words) ===")
    for d in corpus:
        print(d.doc_id, bag_of_words(d, vocab, use_lucene=True))


def demonstrate_inverted_index(corpus: Corpus):
    print("\n=== Inverted index ===")
    idx = InvertedIndex()
    idx.build(corpus, use_lucene=True)
    for term in idx.vocabulary()[:10]:
        print(term, "->", idx.postings(term))


def demonstrate_term_document_matrix(corpus: Corpus):
    print("\n=== Term-document incidence matrix ===")
    terms, docs, mat = term_document_matrix(corpus, use_lucene=True)
    print("terms:", terms)
    print("docs:", docs)
    print("matrix:")
    for row in mat:
        print(row)
    print("\n=== TF-IDF (optional) ===")
    _, _, tfidf = tf_idf_matrix(corpus, use_lucene=True)
    for row in tfidf:
        print([round(x, 3) for x in row])


if __name__ == "__main__":
    c = sample_corpus()
    demonstrate_text_processing()
    demonstrate_document_representation(c)
    vocab = demonstrate_controlled_vocabulary(c)
    demonstrate_free_text_representation(c, vocab)
    demonstrate_inverted_index(c)
    demonstrate_term_document_matrix(c)


