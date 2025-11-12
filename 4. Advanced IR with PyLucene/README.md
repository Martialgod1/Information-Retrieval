# Advanced IR with PyLucene (Lectures 27–34)

This folder provides runnable demos for:
- Relevance feedback: Rocchio and pseudo relevance feedback (query expansion in VSM)
- Relevance-based language models: RM3-style feedback
- Web search: preprocessing (parsing, segmentation, deduplication via shingling/MinHash), simple crawling, link analysis (PageRank, HITS)

All examples use Docker with `coady/pylucene` and require an index with term vectors enabled (done by the advanced indexer here).

---

## Overview

- **Lectures 27–29 (Feedback & Expansion):**
  - Rocchio relevance feedback and pseudo relevance feedback
  - Query expansion in the vector space model (VSM / ClassicSimilarity)
- **Lectures 30–32 (Relevance Models):**
  - Relevance-based language model (RM3-style): build feedback model from top docs and interpolate with original query
- **Lectures 33–34 (Web Search):**
  - Preprocessing: parsing, tokenization, shingling, MinHash LSH near-duplicate detection
  - Crawling (demo)
  - Link analysis: PageRank and HITS

All demos are designed to be minimal, reproducible, and runnable with a few commands.

---

## Quick Start

### 1) Build and shell in
```bash
cd "/Users/pray/Documents/Information-Retrieval/4. Advanced IR with PyLucene"
docker-compose build
```

### 2) Index sample docs (uses term vectors)
```bash
docker-compose run --rm app \
  python3 indexer_advanced.py \
  --source "/app/../3. PyLucene/sample_docs" \
  --index /app/index_tv
```

### 3) Rocchio relevance feedback (pseudo RF)
```bash
docker-compose run --rm app \
  python3 relevance_feedback.py \
  --index /app/index_tv \
  --query "vector space model" \
  --method rocchio \
  --topk 10 \
  --prf-k 5 \
  --expand-terms 10 \
  --alpha 1.0 --beta 0.75 --gamma 0.0
```

### 4) Relevance Model (RM3) feedback
```bash
docker-compose run --rm app \
  python3 relevance_model_lm.py \
  --index /app/index_tv \
  --query "language model" \
  --topk 10 \
  --fb-docs 5 \
  --fb-terms 10 \
  --mu 2000 \
  --lambda 0.6
```

### 5) Web preprocessing: shingling + MinHash dedup
```bash
docker-compose run --rm app \
  python3 web_preprocess.py \
  --source "/app/../3. PyLucene/sample_docs" \
  --shingle-size 5 \
  --minhash-bands 20 \
  --minhash-rows 5 \
  --jaccard-threshold 0.8
```

### 6) Link analysis (PageRank and HITS) on a toy graph
```bash
docker-compose run --rm app \
  python3 link_analysis.py --toy
```

---

## Scripts
- `indexer_advanced.py`: Indexer that stores term vectors on `contents` to enable feedback and expansion.
- `relevance_feedback.py`: Rocchio method and pseudo-relevance feedback with query expansion in VSM.
- `relevance_model_lm.py`: RM3-style relevance model feedback using Dirichlet smoothing and interpolation.
- `web_preprocess.py`: HTML/text parsing, tokenization, shingling, MinHash LSH for near-duplicate detection.
- `crawler.py`: Simple breadth-first crawler (demo; network access may be restricted in some environments).
- `link_analysis.py`: PageRank and HITS on a provided or toy link graph.

---

## Indexing Details (Term Vectors)

- Feedback and expansion rely on access to document-level term statistics.
- `indexer_advanced.py` configures a `FieldType` for `contents` with:
  - `IndexOptions.DOCS_AND_FREQS_AND_POSITIONS`
  - `setStoreTermVectors(True)` and `setStoreTermVectorPositions(True)`
- Re-index your corpus with this indexer to enable all demos.
- Example to index a custom folder:
  ```bash
  docker-compose run --rm app \
    python3 indexer_advanced.py \
    --source "/app/data/my_corpus" \
    --index /app/index_tv
  ```

---

## Relevance Feedback (Rocchio) and Query Expansion

- Command (pseudo RF shown above): selects top-K results as “relevant” automatically.
- Key parameters:
  - `--topk`: number of results to retrieve (and to form non-relevant set)
  - `--prf-k`: number of top docs assumed relevant for feedback
  - `--expand-terms`: number of expansion terms to add
  - `--alpha, --beta, --gamma`: Rocchio weights for original query, relevant centroid, non-relevant centroid
- Notes:
  - Uses VSM with `ClassicSimilarity` for ranking and vector math.
  - Expansion query is built by combining original terms with high-weight feedback terms.
  - To simulate true relevance feedback, you could manually provide doc IDs to treat as relevant/non-relevant (left as an extension).

Example variations:
```bash
# Stronger reliance on feedback
docker-compose run --rm app python3 relevance_feedback.py \
  --index /app/index_tv --query "index compression" --method rocchio \
  --topk 20 --prf-k 8 --expand-terms 15 --alpha 0.8 --beta 1.0 --gamma 0.1
```

---

## Relevance Model (RM3)

- Builds RM1 distribution P(w|R) from top feedback docs using Dirichlet-smoothed P(w|d) and doc weights from base search.
- Interpolates with original query model:
  - `--lambda` is the weight on the original query (typical values 0.5–0.7).
- Key parameters:
  - `--fb-docs`: number of feedback docs
  - `--fb-terms`: number of feedback terms to include
  - `--mu`: Dirichlet smoothing parameter for LM
  - `--lambda`: interpolation weight on original query (RM3)

Example variations:
```bash
docker-compose run --rm app python3 relevance_model_lm.py \
  --index /app/index_tv --query "neural ranking" \
  --fb-docs 10 --fb-terms 20 --mu 1500 --lambda 0.6 --topk 20
```

---

## Web Preprocessing, Shingling, and MinHash LSH

- Pipeline:
  1) Lightweight HTML stripping
  2) Lowercasing, alphanumeric tokenization
  3) k-shingles over tokens
  4) MinHash signatures with banding to generate candidate near-duplicates
  5) Exact Jaccard check to filter candidates above threshold
- Key parameters:
  - `--shingle-size`: k in k-shingles
  - `--minhash-bands`, `--minhash-rows`: LSH banding configuration (num_hashes = bands × rows)
  - `--jaccard-threshold`: final near-duplicate decision threshold

Tips:
- Larger `--shingle-size` reduces false positives but may miss short near-duplicates.
- Adjust `bands` and `rows` to trade off candidate recall vs precision.

---

## Crawling (Demo)

- Minimal BFS crawler to demonstrate focused crawling constraints and link graph construction.
- Network may be restricted; in that case, test against a local HTTP server or skip crawling.
- Usage:
  ```bash
  docker-compose run --rm app \
    python3 crawler.py --seeds https://example.com --max-pages 50 --delay 0.2
  ```
- Options:
  - `--allow-offsite`: allow leaving seed host(s)
  - `--max-pages`: cap number of fetched pages
  - `--delay`: politeness delay between requests

---

## Link Analysis: PageRank and HITS

- `link_analysis.py` runs PageRank and HITS over a small in-memory graph.
- Replace `toy_graph()` with logic to parse edges from a file if desired.
  ```bash
  docker-compose run --rm app python3 link_analysis.py --toy
  ```
- Outputs:
  - PageRank scores per node
  - HITS authority and hub scores per node

---

## Troubleshooting

- Ensure the index was built with term vectors (`indexer_advanced.py`). Without term vectors, feedback scripts will not work.
- PyLucene API differences across versions:
  - Term vectors are accessed via leaf readers. This repo uses `reader.leaves()` and `leaf.reader().getTermVector(localDocId, field)` with a safe fallback.
  - Analyzer token streams must respect the TokenStream contract:
    - Always `reset()`, iterate, `end()`, and `close()` in a `finally` block.
    - `addAttribute` requires `.class_` for PyLucene bindings (e.g., `CharTermAttribute.class_`).
- If crawling fails due to no network, use local/contained HTML files and run `web_preprocess.py` instead.

---

## Notes
- These demos assume English text and use Lucene `StandardAnalyzer`.
- Term vectors are required; always index with `indexer_advanced.py`.
- Crawling may be disabled in restricted environments; use `--seed-file` for offline demos.


