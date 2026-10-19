# SAFE-FOOD Option A - Final pre-push checklist

**Authors:** Mohammad Diab and Mohammad Mantach
**Course:** MSc Knowledge Representation
**Status:** Local main prepared and verified; replace the old main working tree by a normal non-force push after final review.

- [x] Option A prepared: 2,925 OFF-shaped + 797 USDA-shaped synthetic product rows.
- [x] Synthetic data disclaimer clearly visible in README and both reports.
- [x] RDF: 56,474 triples, 3,722 product nodes; 146 candidate barcode overlaps.
- [x] SHACL: zero reported violations and warnings on the prepared graph.
- [x] Docker: Fuseki and access layer running; one-shot pipeline exits with code 0.
- [x] Seven Python tests passed after ML dependencies were persisted in the pipeline Docker image.
- [x] Gemini Live: targeted six-question schema evaluation, mean F1 1.000 for five answerable questions and one correct refusal.
- [x] Mocked repair flow confirmed two attempts and 16 returned brands. No claim of live model repair was made.
- [x] Local .env, model tensor snapshot, backups and LLM cache are ignored by Git.
- [x] Pattern-based source credential scan found no obvious keys; this is not a complete security guarantee.
- [x] Original old-project scripts and historical PDF from data/archive and report/archive removed from current tree.
- [x] Authors added: Mohammad Diab, Mohammad Mantach.
- [ ] Decide whether the course requires individual contributor roles or instructor-specific references (not supplied).
- [ ] Remove superseded report/SAFE_FOOD_Option_A_Technical_Report.pdf from Git before push.
- [ ] Verify git diff --cached --check and git status; commit the final changes.
- [ ] Push to origin/main and inspect the public repository after GitHub confirms success.

**Important:** The older repository's commit history is retained as a parent of the current main branch because it was integrated using a merge. The current main tree is SAFE-FOOD Option A. Removing historical Git objects requires a separate history-rewriting decision and was not requested.

**Data integrity:** OFF and USDA records are synthetic teaching fixtures, not independently validated data from live product databases. Numeric model metrics do not establish real-world food-safety or nutritional validity.
