# SAFE-FOOD - a small, auditable Knowledge Representation project

**Academic focus:** possible ingredient/allergen-tag mismatches in *50 real Open Food Facts yogurt records*, represented in an RDF knowledge graph. This is a **quality-review prototype, not a clinical food-safety checker**. The original synthetic experiment has been replaced as the default data source.

**Project repository (original):** https://github.com/MohammadMantach/Knowledge-Representation-Project  
**Course template:** https://github.com/ahmabboud/kr-team-template  
**Version of this review package:** 2026-10-19. See `CHANGELOG_REVIEW.md` for changes made after the student's uploaded ZIP.

## What's inside

| Layer | File(s) | Truthful status |
|---|---|---|
| Data | `data/real_off_enriched.csv` | 50 real OFF yogurt rows; 48 reported salt values; 2 missing |
| SQL | `data/build_example_sql.py`, `data/example.sql` | Deterministically builds 50 OFF + 42 recognized allergen relations, 0 USDA |
| Ontology | `ontology/foodsafe.ttl`, `ontology/foodon-slim.ttl` | FoodOn identifiers reused in a local slim sketch |
| Mapping | `mapping/mapping.ttl`, `mapping/materialize.py` | Python RDF mapper works; independent R2RML engine NOT verified |
| SHACL | `shapes/shapes.ttl`, `pipeline/run.py` | Pipeline gates before load; pySHACL on Windows previously reported conformance; fresh package should be rerun |
| Learning | `model/` | Train-only imputation, brand-disjoint 3-seed baseline vs graph message passing; exploratory links |
| Access | `access-layer/` | Deterministic no-key offline demo works; Gemini live NOT verified |
| Report | `report/REPORT.md` | Full technical review draft with limits and sources |

See **`START_HERE.md`** for a short Windows run guide and **`TEST_STATUS.md`** for what was and was not actually executed.

## One-command Docker demo (after creating .env)

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose publishes Fuseki on `127.0.0.1:3030` and the access service on `127.0.0.1:8000`. `.env.example` defaults to transparent `LLM_MODE=offline`: its prepared answers are **not Gemini responses**. For genuine AI usage, edit `.env` to set `LLM_MODE=live` and a personal `GOOGLE_API_KEY`; never commit that file.

## Local, no-Docker data + learning path

```powershell
python data/build_example_sql.py
python pipeline/run.py --no-load
python profiling/profiling.py
python rules/rule_checks.py
python model/build_graph.py
python model/baseline.py
python model/gnn.py
python model/link_prediction.py
```

Dependencies for pipeline are in `pipeline/requirements-pipeline.txt` and for access in `access-layer/requirements-access-layer.txt`. ML additionally needs `numpy`, `torch`, `scikit-learn`. For the user's Windows setup, the existing course virtual environment already has these; use it where possible.

### Project limits that must remain visible

- All 50 items are yogurt. No bread/chocolate classification generalization can be claimed.
- Label-gap flags are rule-based review candidates (3 observations) and cannot demonstrate clinical label violation.
- There is **no real USDA feed** in this data package; no ER precision/recall may be claimed.
- A genuine R2RML engine, full Docker stack and a *fresh* live Gemini run need separate verification before Session 8 submission.
