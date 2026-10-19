# Windows verification - SAFE-FOOD Option A

**Updated 20 October 2026 from user-provided PowerShell / Docker output.** The Option A run completed on Windows, using Linux Docker images after a Windows NumPy/scipy application-control issue.

## Confirmed

- `docker compose up -d --build`: Fuseki started; one-shot pipeline exited successfully; access-layer started.
- Pipeline: 56,474 RDF triples; 0 SHACL violations, 0 warnings; 94 VoID triples.
- Fuseki query: 3,722 typed packaged products; 146 synthetic barcode-matched OFF-to-USDA pairs.
- PyTorch and scikit-learn experiments: 3,722 product nodes, 4,264 allergen link declarations; three-seed baseline, GNN, link-ranking outputs saved to `model/outputs/`.
- Permanent pipeline image rebuilt with CPU PyTorch, NumPy, scikit-learn and pytest.
- Final project tests: **7 passed, 2 non-fatal warnings, 97.22s**.
- Gemini live access question generated valid SPARQL with answer 146.
- Live schema QA evaluation after ontology URI prompt fix: F1 1.000 on five answerable questions; one correct refusal. Small, partly targeted suite.
- Simulated two-attempt query-repair loop passed with 16 peanut-allergen brands returned.

## Not yet verified

- Full independent Morph-KGC parity; Protégé reasoner; accuracy on real OFF and USDA products; larger held-out QA evaluation.

**Never include local `.env` or Google API credentials in published files.**
