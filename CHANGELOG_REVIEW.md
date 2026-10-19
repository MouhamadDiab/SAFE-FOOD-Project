# What was changed relative to the uploaded SAFE-FOOD ZIP

1. Default SQL data now comes from the **50 real OFF observations** enriched in the user's Windows workflow; removed synthetic sample rows from the default and set the USDA table to empty instead of claiming artificial ER matches.
2. Restored crucial missing packaging files (`fuseki/Dockerfile`, `.env.example`, `.gitignore`, `.github/workflows/shacl-gate.yml`) and created reproducible lightweight `profiling/`, `rules/`, and `er/` documentation/tools; these folders were absent from the uploaded ZIP because its PowerShell archive command selected only some directories.
3. Corrected `mapping/materialize.py` not to drop invalid records before SHACL. Added a regression test that passes malformed energy to the graph; *actual pySHACL detection on the new package still needs a fresh run*.
4. Expanded the R2RML declaration to cover nutrient, provenance, trace, declared-allergen, Nutri-Score, flagged-gap and optional USDA links. The Python materializer remains the executed implementation; parity with actual R2RML engine is an open task.
5. Replaced `make_void.py` with a simple RDFLib implementation to avoid extra runtime requirements; retained schema validation of declared properties with zero observed triples.
6. Fixed `serve.py` dataset ID (the original mistakenly defaulted to Brunel); improved local Graph execution and added deterministic offline demonstration with clear distinction from Gemini live mode.
7. Replaced unreliable 3-positive label-gap ML objective with binary **reported Nutri-Score A/B vs C/D/E**, using 47 labelled products and 3 seed brand-disjoint splits. Implemented actual neighbor aggregation in `SageLike`, train-only imputation/scaling, saved baseline/GNN scores, and reported small-sample limitations.
8. Made link prediction an explicit heuristic, with held-out edges, popularity and brand-neighbor ranking, and small-vocabulary caveats.
9. Added project README, detailed report, test ledger, defense notes, and automated tests for core local behavior. Does not claim Docker, full pySHACL or live Gemini were verified here.
