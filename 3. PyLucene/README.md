# PyLucene Search Scripts

This folder contains PyLucene search implementations and guides for:
- **Basic retrieval**: BM25, Boolean, VSM, Axiomatic
- **Language Modeling** (Lectures 18-20): Dirichlet and Jelinek-Mercer smoothing
- **Evaluation** (Lectures 23-25): Precision, Recall, MAP, nDCG, MRR

## Contents

### Scripts
- `search_bm25.py` - BM25 ranked retrieval
- `search_boolean.py` - Boolean queries
- `search_vsm.py` - Vector Space Model (TF-IDF)
- `search_axiomatic.py` - Axiomatic retrieval
- `search_lm.py` - Language modeling (Dirichlet/JM)
- `eval_with_pylucene.py` - Evaluation metrics
- `eval_metrics.py` - Utility module for metrics

### Guides
- `lecture_18_20_language_modeling.md` - Language modeling concepts and formulas
- `lecture_21_22_pylucene_search.md` - PyLucene search overview
- `lecture_23_25_evaluation.md` - Evaluation metrics and formulas

---

## Quick Start

### 1. Create the Index

```bash
cd "/Users/pray/Documents/Information-Retrieval/3. PyLucene"
docker-compose run --rm app python3 indexer.py --source "/app" --index /app/index --best-compression
```

### 2. Basic Search Commands

```bash
# BM25 ranked retrieval
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index compression"

# Boolean queries
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "inverted AND index"
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '"vector space" OR compression'

# Vector Space Model (TF-IDF)
docker-compose run --rm app python3 search_vsm.py --index /app/index --query "vector space model" --topk 10

# Axiomatic retrieval (variants: F2EXP | F2LOG | F1EXP | F1LOG)
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "term weighting" --variant F2EXP

# Language Modeling - Dirichlet smoothing
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant dirichlet --mu 2000

# Language Modeling - Jelinek-Mercer smoothing
docker-compose run --rm app python3 search_lm.py --index /app/index --query "language model" --variant jm --lambda 0.2
```

---

## Advanced Examples

### Boolean Query Operators

```bash
# AND operator
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "inverted AND index"

# OR operator
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '"vector space" OR compression'

# NOT operator
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '(vector OR space) AND NOT compression'
```

### BM25 Phrase Queries and Boosting

```bash
# Exact phrase
docker-compose run --rm app python3 search_bm25.py --index /app/index --query '"vector space"'

# Phrase with slop (within 3 positions)
docker-compose run --rm app python3 search_bm25.py --index /app/index --query '"vector space"~3'

# Term boosting
docker-compose run --rm app python3 search_bm25.py --index /app/index --query 'vector^2 space'

# Group boosting
docker-compose run --rm app python3 search_bm25.py --index /app/index --query '(vector space)^3 compression'
```

### Comparing Different Retrieval Methods

```bash
Q='vector space model'
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "$Q"
docker-compose run --rm app python3 search_vsm.py     --index /app/index --query "$Q"
docker-compose run --rm app python3 search_bm25.py    --index /app/index --query "$Q"
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F2EXP
docker-compose run --rm app python3 search_lm.py --index /app/index --query "$Q" --variant dirichlet --mu 2000
docker-compose run --rm app python3 search_lm.py --index /app/index --query "$Q" --variant jm --lambda 0.2
```

### Parameter Tuning

#### BM25 Parameters (k1, b)
```bash
Q='index compression'
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "$Q" --k1 0.5  --b 0.2
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "$Q" --k1 1.2  --b 0.75
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "$Q" --k1 2.0  --b 0.95
```

#### Language Modeling Parameters

**Dirichlet (mu):**
```bash
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant dirichlet --mu 500
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant dirichlet --mu 2000
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant dirichlet --mu 3000
```

**Jelinek-Mercer (lambda):**
```bash
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant jm --lambda 0.1
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant jm --lambda 0.2
docker-compose run --rm app python3 search_lm.py --index /app/index --query "information retrieval" --variant jm --lambda 0.4
```

#### Axiomatic Variants
```bash
Q='term weighting'
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F2EXP
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F2LOG
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F1EXP
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "$Q" --variant F1LOG
```

### Other Options

```bash
# Change number of results
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index" --topk 20

# Change search field
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index" --field contents
```

---

## Evaluation

### Basic Evaluation (See Retrieved Documents)

```bash
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "vector space model" \
  --similarity bm25 \
  --topk 10
```

### Evaluation with Relevance Judgments

**By position (rank order):**
```bash
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "vector space model" "information retrieval" \
  --relevance "vector space model:1,0,1,0,0,0,0,0,0,0" "information retrieval:0,1,1,0,0,0,0,0,0,0" \
  --similarity bm25 \
  --topk 10
```

**By document path:**
```bash
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "vector space model" \
  --doc-relevance "sample_docs/vsm_mixed.txt:1 sample_docs/boost_vector.txt:1" \
  --similarity bm25 \
  --topk 10
```

### Compare Different Similarities

```bash
# BM25
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "language model" "query likelihood" \
  --relevance "language model:1,1,0,0,0" "query likelihood:1,0,1,0,0" \
  --similarity bm25 \
  --topk 5

# Dirichlet
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "language model" "query likelihood" \
  --relevance "language model:1,1,0,0,0" "query likelihood:1,0,1,0,0" \
  --similarity dirichlet \
  --mu 2000 \
  --topk 5

# Jelinek-Mercer
docker-compose run --rm app python3 eval_with_pylucene.py \
  --index /app/index \
  --queries "language model" "query likelihood" \
  --relevance "language model:1,1,0,0,0" "query likelihood:1,0,1,0,0" \
  --similarity jm \
  --lambda 0.2 \
  --topk 5
```

---

## Notes

- Ensure Docker Desktop is running before executing commands
- The container mounts the project at `/app`; all paths in commands use that mount
- Use `--topk`, `--field`, or method-specific parameters to experiment
- For pre-processing details (tokenization, stemming), see `indexer.py`
- **Important for evaluation**: Without relevance judgments, all metrics will be 0

---

## Learn More

For detailed explanations, formulas, and concepts, see the guide files:
- **Language Modeling**: `lecture_18_20_language_modeling.md`
- **PyLucene Search**: `lecture_21_22_pylucene_search.md`
- **Evaluation Metrics**: `lecture_23_25_evaluation.md`
