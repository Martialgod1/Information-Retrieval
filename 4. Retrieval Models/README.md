## Retrieval Models (Boolean, VSM, Ranked, Term Weighting)

This module introduces classical retrieval models and term weighting, with simple runnable examples.

Included topics:
- Boolean retrieval (AND/OR/NOT)
- Vector Space Model (VSM) with cosine similarity
- Ranked retrieval via TF‑IDF cosine and BM25
- Term weighting: TF, IDF, TF‑IDF, BM25 components
- Brief axiomatic view for term weighting

Run the demo:
```bash
cd "4. Retrieval Models"
python3 run_retrieval_demo.py
```

Files:
- `boolean_model.py` – Boolean set retrieval over postings
- `weighting.py` – TF, IDF, TF‑IDF, BM25 utilities
- `vsm.py` – Vector space model with cosine similarity
- `ranked.py` – TF‑IDF cosine ranking and BM25 ranking
- `run_retrieval_demo.py` – End-to-end example

### Axiomatic Justification (very brief)
Under axiomatic IR, desirable properties (axioms) for term weighting/scoring functions imply forms like IDF and term saturation:
- Terms that appear in many documents carry less discriminative power → inverse document frequency
- Additional occurrences have diminishing returns → log/concave TF or BM25 saturation `tf / (tf + k)`
- Longer documents shouldn’t be unfairly advantaged → length normalization
BM25 can be seen as satisfying such axioms: concavity in TF, IDF monotonicity, and normalization by document length.


