import argparse
import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path


def read_texts(sources):
    for src in sources:
        p = Path(src)
        if p.is_dir():
            for root, _dirs, files in os.walk(p):
                for f in files:
                    fp = Path(root) / f
                    if fp.suffix.lower() in {".txt", ".md", ".html", ".htm"}:
                        try:
                            yield str(fp), fp.read_text(encoding="utf-8", errors="ignore")
                        except Exception:
                            continue
        elif p.is_file():
            try:
                yield str(p), p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue


def strip_html(text: str) -> str:
    # Very lightweight HTML tag removal
    return re.sub(r"<[^>]+>", " ", text)


def tokenize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if t]


def shingles(tokens, k: int):
    for i in range(0, max(0, len(tokens) - k + 1)):
        yield tuple(tokens[i : i + k])


def minhash_signature(shingle_set, num_bands: int, rows_per_band: int):
    # Simple MinHash using multiple hash functions derived from stable hashing + salts
    # Returns list of band hashes
    if not shingle_set:
        return []
    signature = []
    band_hashes = []
    num_hashes = num_bands * rows_per_band
    # Build num_hashes minhash values
    min_vals = [2**64 - 1] * num_hashes
    shingles_strings = [" ".join(s) for s in shingle_set]
    for sh in shingles_strings:
        for i in range(num_hashes):
            salt = f"h{i}"
            h = hashlib.blake2b((salt + sh).encode("utf-8"), digest_size=8).digest()
            val = int.from_bytes(h, "big")
            if val < min_vals[i]:
                min_vals[i] = val
    # Banding
    for b in range(num_bands):
        start = b * rows_per_band
        end = start + rows_per_band
        chunk = min_vals[start:end]
        band_digest = hashlib.blake2b((",".join(map(str, chunk))).encode("utf-8"), digest_size=8).hexdigest()
        band_hashes.append(band_digest)
    return band_hashes


def lsh_candidates(doc_to_bands: dict):
    bucket_to_docs = defaultdict(list)
    for doc, bands in doc_to_bands.items():
        for band_id, band_hash in enumerate(bands):
            bucket_to_docs[(band_id, band_hash)].append(doc)
    candidates = set()
    for _bucket, docs in bucket_to_docs.items():
        if len(docs) > 1:
            docs = sorted(docs)
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    candidates.add((docs[i], docs[j]))
    return candidates


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / max(1, union)


def main():
    parser = argparse.ArgumentParser(description="Web preprocessing: parsing, shingling, MinHash deduplication")
    parser.add_argument("--source", nargs="+", required=True, help="Files or directories")
    parser.add_argument("--shingle-size", type=int, default=5, help="Shingle size k")
    parser.add_argument("--minhash-bands", type=int, default=20, help="Number of bands")
    parser.add_argument("--minhash-rows", type=int, default=5, help="Rows per band")
    parser.add_argument("--jaccard-threshold", type=float, default=0.8, help="Near-duplicate threshold")
    args = parser.parse_args()

    docs = []
    for path, text in read_texts(args.source):
        clean = strip_html(text)
        tokens = tokenize(clean)
        sset = set(shingles(tokens, args.shingle_size))
        docs.append((path, sset))

    doc_to_bands = {}
    for path, sset in docs:
        doc_to_bands[path] = minhash_signature(sset, args.minhash_bands, args.minhash_rows)
    candidates = lsh_candidates(doc_to_bands)

    print(f"Docs read: {len(docs)}")
    print(f"Candidate pairs from LSH: {len(candidates)}")

    near_dups = []
    for a, b in sorted(candidates):
        aset = dict(docs)[a]
        bset = dict(docs)[b]
        jac = jaccard(aset, bset)
        if jac >= args.jaccard_threshold:
            near_dups.append((a, b, jac))

    if near_dups:
        print("\nNear-duplicates (Jaccard >= threshold):")
        for a, b, jac in near_dups:
            print(f"{a}  ~  {b}  (J={jac:.3f})")
    else:
        print("\nNo near-duplicates above threshold.")


if __name__ == "__main__":
    main()


