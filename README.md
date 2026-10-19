# SAFE-FOOD - Option A (synthetic two-source knowledge graph)

**MSc Knowledge Representation teaching project - verification snapshot: 20 October 2026.**

**Authors:** Mohammad Diab and Mohammad Mantach.

SAFE-FOOD illustrates ontology-driven quality checking, semantic integration, SPARQL question-answering and exploratory graph learning over two **synthetic** packaged-food datasets shaped like Open Food Facts (OFF) and USDA FoodData Central (USDA). These are **not verified real product downloads**. Barcodes and overlap pairs were constructed for a controlled teaching experiment. Do not use the outputs for consumer, clinical or regulatory food-safety decisions.

**Start here:** [Windows / Docker run guide](RUN_GUIDE_AR.md) | [Technical report](report/REPORT.md) | [PDF report](report/SAFE_FOOD_Option_A_Final_Report.pdf) | [Validation ledger](TEST_STATUS.md) | [Before GitHub](FINAL_PREUPLOAD_CHECKLIST.md).

## Architecture

`Synthetic OFF/USDA CSV -> quality preparation -> SQLite -> RDF materialization + FoodOn-based ontology -> SHACL -> Fuseki/SPARQL -> English-to-SPARQL Gemini access`

A separate graph-learning experiment reads RDF-derived features: `RDF -> nutrition and brand-neighbor graph -> logistic-regression baseline / unchanged GraphSAGE-style GNN`. The GNN does **not** detect allergen violations; rule-based review flags and SHACL are separate stages.

| Component | Source |
| --- | --- |
| Immutable synthetic source files | `data/raw/off_products_original.csv`, `data/raw/usda_products_original.csv` |
| Preparation, audit and SQLite | `data/prepare_option_a.py`, `data/quality/`, `data/build_example_sql.py` |
| Application ontology / reused identifier subset | `ontology/foodsafe.ttl`, `ontology/foodon-slim.ttl` |
| RDF mapper / declarative R2RML | `mapping/materialize.py`, `mapping/mapping.ttl` |
| SHACL and review rules | `shapes/`, `rules/` |
| Pipeline and Fuseki | `pipeline/run.py`, `docker-compose.yml`, `/kr` endpoint |
| Question answering | `access-layer/` (offline demonstration and live Gemini) |
| Graph learning | `model/build_graph.py`, `model/baseline.py`, `model/gnn.py`, `model/link_prediction.py` |
| Experiments | `model/outputs/{baseline,gnn,link-prediction}.csv` |

## Observed results (verified on a Windows Docker run)

| Measure | Result |
| --- | ---: |
| Raw OFF-shaped / USDA-shaped | 3,001 / 800 rows |
| Prepared OFF-shaped / USDA-shaped | 2,925 / 797 rows |
| Total RDF `PackagedProduct` nodes | 3,722 |
| RDF triples | 56,474 |
| Distinct exact-barcode OFF-to-USDA pairs | 146 |
| Directed `sameProductAs` assertions | 292 (symmetric) |
| Declared allergen links | 4,264 across 12 known types |
| SHACL violations / warnings | 0 / 0 on prepared RDF |
| Project unit tests | 7 passed, 0 skipped; two non-fatal RDFLib UTF-8 warnings |
| Nutri-Score-labelled OFF nodes | 1,945 (758 A/B; 1,187 C/D/E) |
| GNN mean Macro-F1, three brand-disjoint seeds | 0.5069 |
| Logistic regression mean Macro-F1 | 0.5062 |
| Live Gemini `schema` mean F1, after targeted ontology-name fix | 1.000 on **five** answerable questions |
| Correct live refusals | 1 / 1 on the tiny evaluation suite |

The GNN did **not** show a meaningful improvement over the baseline on these synthetic labels. The strong live Gemini result describes one small, partly targeted test suite, **not general accuracy**. `examples` and `repair` configurations were measured **before** the latest prompt/validator update (0.688 each), not repeated afterward. A deterministic scripted repair simulation succeeded in 2 attempts and returned 16 distinct peanut-allergen brand names; this does **not** establish that a real Gemini call needed repair.

## Quick start - Docker Desktop

Requirements: Git is needed only for later version control; Docker Desktop with Linux containers runs the stack on Windows. Copy `.env.example` to `.env` and leave API credentials blank for the offline demo.

```powershell
cd "C:\Users\Moudi\Desktop\M2\KRR\SAFE-FOOD-OPTION-A-READY"
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d --build
# The pipeline runs once and exits 0 on success; Fuseki and access-layer stay up.
docker compose ps -a
docker compose logs pipeline --tail 40
```

Fuseki: http://127.0.0.1:3030, dataset `kr`. Access layer: http://127.0.0.1:8000.

```powershell
# Regression tests, including the PyTorch-dependent test:
docker compose run --rm --no-deps pipeline python -m pytest -q tests/

# Inspect SPARQL-backed answers:
docker compose exec -T access-layer python ask.py "How many OFF products are linked to a USDA product via sameProductAs?"
```

The pipeline Docker image must contain `numpy`, `scikit-learn`, `pytest` and the CPU build of `torch` for all seven tests to run. The complete guide includes the verified installation approach. With `LLM_MODE=offline`, answers are scripted teaching examples, **not Gemini inference**. To test real Gemini: set `LLM_MODE=live` and `GOOGLE_API_KEY` privately inside `.env`, recreate the access-layer service, and use `ask.py` or `evaluate.py`. Gemini calls may have rate limits or costs.

### SPARQL verification

```sparql
PREFIX fs: <https://ul.edu.lb/kr/foodsafe#>
SELECT (COUNT(DISTINCT ?p) AS ?products)
WHERE { ?p a fs:PackagedProduct . }
```

Expected: 3,722 products. For exact-code source matches:

```sparql
PREFIX fs: <https://ul.edu.lb/kr/foodsafe#>
SELECT (COUNT(DISTINCT ?off) AS ?pairs)
WHERE {
  ?off fs:fromSource fs:SourceOFF ; fs:sameProductAs ?usda .
  ?usda fs:fromSource fs:SourceUSDA .
}
```

Expected: 146 distinct OFF product matches.

## Reproducibility, limitations and safety

The repository contains original synthetic inputs and reproducible preparation scripts. `data/fetch_or_build_sample.py` is a **legacy generator**; do not run it over Option A prepared inputs. Preserve and disclose missing nutrition fields: missing is not zero. The application ontology plus a limited FoodOn identifier subset does not constitute the full FoodOn ontology. `sameProductAs` joins do not mean independently verified real-world identity. The GNN aggregates brand-neighbor features, **not** `sameProductAs` or allergen edges.

`mapping/mapping.ttl` is a declarative R2RML counterpart. Independent parity against Morph-KGC, Protégé reasoning, and fresh-real-data validation are still optional **unverified** extensions and must not be claimed as completed.

**Secrets:** keep `.env` private; do not share an API key, commit `.env`, or publish recorded live-response caches. See [final checklist](FINAL_PREUPLOAD_CHECKLIST.md). This update does **not** push to GitHub or modify Python model/ontology/dataset files.
