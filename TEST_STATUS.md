# Verification ledger - 2026-10-19

**Directly executed here (Python 3.13 environment, no network/ Docker):**

- Rebuilt committed `data/example.sql` from the included real 50-product CSV: 50 OFF rows, 42 declared-allergen relationship rows, 0 USDA.
- Materialized `build/graph.nt` from SQLite: 813 RDF triples and 50 typed products.
- Generated `build/void.ttl` with local RDFLib: 75 VoID triples; checked ontology/SHACL/R2RML Turtle parses.
- Checked 48/50 salt present, 24 numeric zeros, 2 truly missing.
- Three-seed LogisticRegression and GraphSAGE-like Node Classification, with brand-disjoint train/test partitions and train-only preprocessing. Numeric outputs are committed as CSV in `model/outputs/`.
- Three-seed exploratory product/allergen link ranker vs popularity baseline. Outputs in `model/outputs/link-prediction.csv`.
- Deterministic `LLM_MODE=offline`: 5/5 gold answer sets matched, 1/1 unanswerable medical question refused. **Not a Gemini result**.
- Local pytest: 5 passed, 1 skipped, with skipped test needing missing `pyshacl` package. The original user's Windows screenshots before the file review showed real pySHACL conforms on the real sample and an injected missing-barcode failure, but these are **not a direct fresh run of this new package**.

**Not independently executed here:**

- `docker compose up --build`, remote Fuseki/HTTP contract, or actual packaged service startup (Docker not available).
- `pyshacl` on the revised mapper output (dependency unavailable in this runtime; provided CI workflow includes it).
- Live Gemini API evaluation (key/network not provided).
- A Morph-KGC R2RML engine; the tested default is Python materialization, not the declared mapping file.
- Any cross-source entity resolution (USDA table deliberately empty).
- Reasoner run in Protégé/ELK/HermiT (ontologies were only parsed successfully with RDFLib).

**Interpreting scores:** The tiny, one-category sample means all classification and ranking scores are exploratory. Offline access F1=1.0 is built from fixed templates, not evidence of LLM generalization. Do not include metrics from the previous synthetic-data version in results for this build.
