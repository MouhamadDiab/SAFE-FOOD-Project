# Option A change log - 2026-10-19

- Switched to the user's **synthetic** original two CSVs (3,001 OFF-shaped + 800 USDA-shaped raw).
- Added transparent preparation script and audit with raw SHA256 checksums.
- Prepared 2,925 OFF and 797 USDA records; exact-code overlap 146.
- Added a reverse mapping for foodsafe:sameProductAs to represent the symmetric relationship in R2RML without OWL inferencing.
- Rewrote tests and documentation to match the synthetic Option A data and avoid stale 50-real-yogurt metrics.
- Preserved the original old report PDF under `report/archive/` and retained the former real 50-yogurt CSV in `data/archive/`.
- **No modifications** to GNN, baseline, common split, graph feature builder, link ranker, ontology classes or main pipeline.
