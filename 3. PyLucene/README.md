## PyLucene Search Scripts

This folder contains PyLucene search implementations and guides for:
- Basic retrieval: BM25, Boolean, VSM, Axiomatic
- Language Modeling (Lectures 18-20): Dirichlet and Jelinek-Mercer smoothing
- Evaluation (Lectures 23-25): Precision, Recall, MAP, nDCG, MRR

### Scripts
- `search_bm25.py` - BM25 ranked retrieval
- `search_boolean.py` - Boolean queries
- `search_vsm.py` - Vector Space Model (TF-IDF)
- `search_axiomatic.py` - Axiomatic retrieval
- `search_lm.py` - Language modeling (Dirichlet/JM)
- `eval_with_pylucene.py` - Evaluation metrics
- `eval_metrics.py` - Utility module for metrics

### Guides
- `lecture_18_20_language_modeling.md` - Language modeling concepts
- `lecture_21_22_pylucene_search.md` - PyLucene search overview
- `lecture_23_25_evaluation.md` - Evaluation metrics

---

## Run to Create the indexes
```bash
cd "/Users/pray/Documents/Information-Retrieval/3. PyLucene"
docker-compose run --rm app python3 indexer.py --source "/app" --index /app/index --best-compression
```

```bash
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index compression"
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "inverted AND index"
docker-compose run --rm app python3 search_vsm.py --index /app/index --query "vector space model" --topk 10
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "term weighting" --variant F2EXP

# Language Modeling (LM) retrieval
# Dirichlet smoothing (mu)
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant dirichlet --mu 2000
# Jelinek–Mercer smoothing (lambda)
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant jm --lambda 0.2
```





Explore More
```bash
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "inverted AND index"
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '"vector space" OR compression'
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '(vector OR space) AND NOT compression'


docker-compose run --rm app python3 search_bm25.py --index /app/index --query '"vector space"'        # exact phrase
docker-compose run --rm app python3 search_bm25.py --index /app/index --query '"vector space"~3'      # phrase with slop (within 3 positions)

docker-compose run --rm app python3 search_bm25.py --index /app/index --query 'vector^2 space'        # boost 'vector'
docker-compose run --rm app python3 search_bm25.py --index /app/index --query '(vector space)^3 compression'


Q='vector space model'
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "$Q"
docker-compose run --rm app python3 search_vsm.py     --index /app/index --query "$Q"
docker-compose run --rm app python3 search_bm25.py    --index /app/index --query "$Q"
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F2EXP

docker-compose run --rm app python3 search_lm.py --index /app/index --query "$Q" --variant dirichlet --mu 2000

docker-compose run --rm app python3 search_lm.py --index /app/index --query "$Q" --variant jm --lambda 0.2

Q='index compression'
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "$Q" --k1 0.5  --b 0.2
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "$Q" --k1 1.2  --b 0.75
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "$Q" --k1 2.0  --b 0.95

Q='term weighting'
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F2EXP
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F2LOG
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F1EXP
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F1LOG


docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index" --topk 20
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index" --field contents

## Lectures 18–20: Language Modeling for IR

### Overview
Language Modeling (LM) for IR ranks documents by how likely they are to have generated the query. Core variants:
- Query Likelihood (QL)
- KL Divergence Retrieval Model (LM-IR via relative entropy)
- Smoothing: Dirichlet and Jelinek–Mercer (JM)

---

### Query Likelihood (Unigram LM)
Goal: rank documents by P(q | d), assuming query terms are generated from a document language model.

- Unigram, bag-of-words model, usually with independence over query terms.
- With smoothing, for query q = [t1, t2, ..., tk]:

P(q | d) = ∏_{t∈q} P(t | d)

Where P(t | d) is a smoothed probability derived from counts in document d and the collection.

---

### Smoothing
Smoothing is crucial to avoid zero probabilities and to regularize sparse estimates.

1) Dirichlet Prior Smoothing

P(t | d) = ( c(t, d) + μ · P(t | C) ) / ( |d| + μ )

- c(t, d): count of term t in document d
- |d|: document length
- P(t | C): collection language model (e.g., total counts in corpus / total tokens)
- μ: hyperparameter (common range: 500–3000) controlling strength of collection prior

Notes:
- When |d| is small, more mass shifts to P(t | C).
- Works well in practice; μ is typically tuned on validation.

2) Jelinek–Mercer (JM) Interpolation

P(t | d) = (1 − λ) · P_ML(t | d) + λ · P(t | C)

- P_ML(t | d) = c(t, d) / |d|
- λ ∈ [0, 1] (commonly ~0.1–0.4)

Notes:
- Simpler, linear interpolation.
- Higher λ increases reliance on collection model.

Scoring Tip: Work in log-space to avoid underflow:

score(d, q) = Σ_{t∈q} log P(t | d)

---

### KL Divergence Retrieval
Rank by divergence between the query model and the document model:

score(d, q) = − KL( P(·|q) || P(·|d) ) = − Σ_t P(t|q) · log( P(t|q) / P(t|d) )

- P(t|q): query model (often ML estimate: term frequency in query / |q|)
- P(t|d): smoothed document model (Dirichlet or JM)
- Equivalent to a cross-entropy ranking up to a constant; requires smoothing of P(t|d)

Notes:
- If P(t|q) is ML, terms not in q have zero mass and drop out.
- With Dirichlet/JM, LM-IR KL and QL are closely related and often perform similarly.

---

### Run with PyLucene (Dirichlet / JM)
Use Lucene's LM similarities via the provided script:
```bash
cd "3. PyLucene"
# Dirichlet smoothing
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant dirichlet --mu 2000
# Jelinek–Mercer smoothing
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant jm --lambda 0.2

# Compare different mu values for Dirichlet
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant dirichlet --mu 500
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant dirichlet --mu 2000
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant dirichlet --mu 3000

# Compare different lambda values for JM
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant jm --lambda 0.1
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant jm --lambda 0.2
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant jm --lambda 0.4
```

---

### Minimal Worked Example (Dirichlet)
Given query q = ["language", "model"], document d with counts:
- c(language, d) = 2, c(model, d) = 1, |d| = 100
- Collection: P(language|C) = 0.0005, P(model|C) = 0.0007
- μ = 2000

Compute:
- P(language|d) = (2 + 2000·0.0005) / (100 + 2000)
- P(model|d)    = (1 + 2000·0.0007) / (100 + 2000)
- score(d, q)   = log P(language|d) + log P(model|d)

---

```

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

## Lectures 23–25: Evaluation

### Overview
Covers evaluation fundamentals and commonly used IR metrics, forums and their roles, and statistical testing for comparing systems.

---

### Confusion Matrix (Binary Classification Context)
For a query–document judgment (relevant vs not relevant):
- True Positive (TP): relevant and retrieved
- False Positive (FP): not relevant but retrieved
- False Negative (FN): relevant but not retrieved
- True Negative (TN): not relevant and not retrieved

While IR ranking often focuses on the top-k list rather than global TNs, TP/FP/FN underpin precision/recall.

---

### Core Metrics
- Precision@k = (# relevant in top-k) / k
- Recall@k = (# relevant in top-k) / (# relevant in collection for the query)
- Average Precision (AP): average of precision at each rank where a relevant is found
- Mean Average Precision (MAP): mean of AP over queries
- nDCG@k: DCG@k / IDCG@k, where DCG@k = Σ_{i=1..k} (gain_i / log2(i+1)), gain often = relevance grade
- MRR: mean of 1 / rank of first relevant over queries

Notes:
- Choose cutoff k appropriate to your task (e.g., 10 or 20 for web search).
- Use graded relevance for DCG/nDCG; binary relevance for AP, MRR.

---

### Other Common Metrics
- F1@k: harmonic mean of Precision@k and Recall@k
- R-Precision: Precision at R, where R is the number of relevant documents for the query
- AUC-ROC / PR curves: more common in classification; PR curve is informative for IR with class imbalance

---

### Evaluation Forums and Their Roles
- TREC: drives shared tasks and datasets; standard test collections, topics, and relevance judgments
- CLEF, NTCIR, FIRE, and others: regional and domain-specific evaluations
- Roles: establish common benchmarks, reproducibility, and fair comparisons across systems

---

### Statistical Significance Testing (Pairwise)
Goal: determine if observed metric differences between two systems are unlikely due to chance.

Common tests over per-query metric values (e.g., AP per query):
- Paired t-test: assumes approximately normal differences; widely used
- Wilcoxon signed-rank test: non-parametric alternative
- Randomization (random/permutation) test: minimal assumptions; robust and recommended

Procedure:
1) Compute a per-query metric (e.g., AP) for each system.
2) Obtain per-query differences.
3) Apply a paired test to these differences; report p-value.
4) Correct for multiple comparisons if testing many pairs (e.g., Holm–Bonferroni).

Reporting:
- Always report mean metric and a test with p-value (e.g., p < 0.05).
- Include effect size when possible.

---

### Minimal Pseudocode Snippets
Precision@k and Recall@k (binary relevance list `rels` of length k):
```text
precision_at_k = sum(rels[:k]) / k
recall_at_k    = sum(rels[:k]) / num_relevant_total
```

Average Precision (AP) given ranked binary relevance `rels`:
```text
ap = mean( precision_at_k(i) for i where rels[i] == 1 )
```

nDCG@k with graded relevance `g[i]`:
```text
dcg  (Discounted Cumulative Gain): = sum( g[i] / log2(i+2) for i in 0..k-1 )
idcg = dcg of ideal sorted gains
ndcg = dcg / idcg if idcg > 0 else 0
```

---

### Run Evaluation with PyLucene
Use the PyLucene evaluation script to run queries and compute metrics:

**Important:** Without relevance judgments, all metrics will be 0. You must provide relevance judgments.

```bash
cd "3. PyLucene"
# With relevance judgments by position (1=relevant, 0=not relevant for each rank)
# Format: "query:rel1,rel2,rel3,..."
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "vector space model" "information retrieval" \
  --relevance "vector space model:1,0,1,0,0,0,0,0,0,0" "information retrieval:0,1,1,0,0,0,0,0,0,0" \
  --similarity bm25 \
  --topk 10

# With relevance judgments by document path (more practical)
# First check what documents are retrieved, then mark them as relevant
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "vector space model" \
  --doc-relevance "sample_docs/vsm_mixed.txt:1 sample_docs/boost_vector.txt:1" \
  --similarity bm25 \
  --topk 10

# Compare different similarities
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "language model" "query likelihood" \
  --relevance "language model:1,1,0,0,0" "query likelihood:1,0,1,0,0" \
  --similarity dirichlet \
  --mu 2000 \
  --topk 5

docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "language model" "query likelihood" \
  --relevance "language model:1,1,0,0,0" "query likelihood:1,0,1,0,0" \
  --similarity jm \
  --lambda 0.2 \
  --topk 5
```

### Utility Module
The `eval_metrics.py` module provides metric functions for import:
```python
from eval_metrics import precision_at_k, recall_at_k, average_precision, mean_average_precision, ndcg_at_k, mrr
```

---
