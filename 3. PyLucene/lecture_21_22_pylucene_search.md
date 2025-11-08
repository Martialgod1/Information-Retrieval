## Lectures 21–22: Searching with PyLucene

### Overview
This guide shows how to run and explore search with PyLucene using the scripts in `3. PyLucene`.

---

### Quick Start
From the project root:

```bash
cd "3. PyLucene"
```

Create/refresh the index (best-compression falls back if unavailable):
```bash
docker-compose run --rm app python3 indexer.py --source "/app" --index /app/index --best-compression
```

Run searches:
```bash
# BM25 ranked retrieval
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index compression"

# Boolean queries
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "inverted AND index"
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '"vector space" OR compression'

# Vector Space Model (TF–IDF)
docker-compose run --rm app python3 search_vsm.py --index /app/index --query "vector space model" --topk 10

# Axiomatic retrieval (variants: F2EXP | F2LOG | F1EXP | F1LOG)
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "term weighting" --variant F2EXP

# Language Modeling (Dirichlet)
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant dirichlet --mu 2000

# Language Modeling (Jelinek–Mercer)
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant jm --lambda 0.2
```

See more examples in `3. PyLucene/README.md` including phrase queries with slop, term boosting, field selection, and parameter sweeps for BM25.

---

### Notes
- Ensure Docker Desktop is running.
- The container mounts the project at `/app`; paths in commands use that mount.
- Use `--topk`, `--field`, or method-specific params (BM25: `--k1`, `--b`; LM: `--mu`, `--lambda`) to experiment.
- For pre-processing decisions (tokenization, stemming), consult the indexer implementation in `3. PyLucene/indexer.py`.

---

### Tips
- Keep an eye on analysis chain (token filters) to match your query formulation.
- Compare BM25 vs VSM vs Axiomatic vs LM results on the same queries to understand behavior.
- Use small test corpora to iterate quickly; then scale up.
