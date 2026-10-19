# SAFE-FOOD Option A - test and evaluation ledger

**User-executed Windows Docker evidence, 19-20 October 2026.** Each result here was provided as terminal output in the project walkthrough. Results not tested are marked separately.

| Check | Observed result | Scope |
| --- | --- | --- |
| Data preparation | 2,925 prepared OFF / 797 USDA | Synthetic fixtures |
| SQLite | 4,264 declared allergen rows | Synthetic fixtures |
| RDF materialization | 56,474 triples; 3,722 typed products | Python materializer |
| VoID | 94 triples | Pipeline run |
| pySHACL gate | 0 violations; 0 warnings | Prepared graph only |
| Fuseki SELECT | 3,722 products | Live endpoint |
| Cross-source SELECT | 146 distinct OFF-to-USDA barcode pairs | Live endpoint |
| Python ML learning | Baseline + GNN + link ranking outputs saved | Three random seeds |
| First unit-test run | 6 passed, 1 skipped | Before permanent torch installation |
| Final unit-test run | **7 passed, 0 skipped, 0 failed** | 2 non-fatal `rdflib` UTF-8 notices; 97.22 seconds |
| Gemini live matched product question | 146 | Live mode; API key configured privately |
| Live Gemini before targeted fix: schema | F1 0.800 on 5 answerable, 1/1 correct refusals | Six-question test suite |
| Live Gemini before targeted fix: examples / repair | 0.688 / 0.688 | These two modes not rerun after fix |
| Live Gemini after prompt and validator fix: schema | **F1 1.000 on 5 answerable; 1/1 correct refusal** | No actual live repair was needed |
| Peanut allergen query after fix | 16 distinct brands | Fuseki and live Gemini |
| Controlled simulated repair | Two attempts; malformed URI caught; 16 brands returned | Mock model; tests loop but not live LLM repair |

Observed GNN Macro-F1 (seeds 11 / 23 / 37): 0.5211 / 0.4957 / 0.5038, mean **0.5069**. Baseline: 0.5062 / 0.4830 / 0.5293, mean **0.5062**. The numerical gap is very small, and all labels are synthetic. GNN results are not the same measure as Gemini QA F1.

### Unverified or incomplete

- Morph-KGC vs Python RDF full graph parity is not established here.
- Protégé reasoner consistency not independently checked here.
- Real-world OFF-USDA identity accuracy / consumer product provenance not established.
- Full quality of text-to-SPARQL on a broad held-out benchmark not established; current test set is small and targeted.
- Reproducibility on an unrelated fresh Windows machine or external CI has not been independently demonstrated.

Do not claim a perfect real-world classifier, clinical allergy checker or food-safety decision engine.
