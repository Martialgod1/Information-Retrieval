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
```