## Index Structures (Creation, Compression, Queries)

This section explains how to build an inverted index, compress posting lists, and execute basic boolean queries. Code is educational and small, designed to pair with the "Basics of IR" module.

What you will find here:
- Index creation: posting lists with positions and document lengths
- Index compression: gap encoding + variable-byte (VB) coding
- Query execution: AND / OR over postings; simple scoring via term frequency

How to run:
```bash
cd "3. Index Structures"
python3 run_index_demo.py
```

Files:
- `vb_codec.py` – Variable-byte encode/decode and gap utilities
- `index_builder.py` – Build index, optional compression
- `query_engine.py` – Boolean query execution over (compressed) postings
- `run_index_demo.py` – End-to-end example

Notes:
- Compression is optional; you can run queries on raw postings or compressed postings.
- Variable-byte coding is a standard educational codec for integer sequences.


