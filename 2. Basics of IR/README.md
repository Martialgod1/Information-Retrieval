## Basics of Information Retrieval

This module demonstrates core IR building blocks with simple, readable Python implementations and optional PyLucene-powered tokenization.

Topics covered:
- Document representation
- Controlled vocabulary
- Free text representation (bag-of-words, term frequency)
- Inverted index (with positions)
- Term–document incidence matrix (+ optional TF‑IDF)
- Text processing: tokenization, stopword removal, stemming, lemmatization

How to run examples:
1) With your system Python:
   ```bash
   cd "2. Basics of IR"
   python3 run_examples.py
   ```

2) Inside your PyLucene container (optional):
   - Ensure the project root is available in the container at `/workspace` (mount or copy the folder)
   - Then run:
   ```bash
   cd "/workspace/2. Basics of IR"
   python3 run_examples.py
   ```


