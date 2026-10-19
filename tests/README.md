# Option A regression tests

`python -m pytest -q tests/` after building `data/example.sql` and `build/graph.nt`. Test the prepared synthetic CSV counts, original raw retention, RDF typed nodes and bidirectional sameProductAs, TTL syntax, deliberately injected 999 kcal/100g SHACL failure (requires pySHACL), offline query + refusal and GNN mean-message behavior (torch optional). With pySHACL missing, a test is skipped; this is **not** validation of SHACL success.

For a manual SHACL negative-case demo that leaves all data unchanged, run `python data/demo_bad_shacl.py`.
