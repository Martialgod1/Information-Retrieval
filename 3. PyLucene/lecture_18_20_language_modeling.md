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
