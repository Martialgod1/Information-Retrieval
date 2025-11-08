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
