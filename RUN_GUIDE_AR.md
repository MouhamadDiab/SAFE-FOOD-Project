# SAFE-FOOD Option A - verified Windows / Docker run guide

**Snapshot: 20 October 2026.** Both OFF-shaped and USDA-shaped inputs are **synthetic** teaching fixtures. The validated prepared graph has 3,722 typed products, including 2,925 OFF and 797 USDA records. This guide replaces outdated Option A validation-pending notes.

## 1. Open the correct project

```powershell
cd "C:\Users\Moudi\Desktop\M2\KRR\SAFE-FOOD-OPTION-A-READY"
```

Do not overwrite or push the separate older SAFE-FOOD-REVIEWED repository. Avoid `data/fetch_or_build_sample.py`: it generates a new synthetic sample and can overwrite the prepared data.

## 2. Start Docker stack

Docker Desktop must be running with Linux containers. Create `.env` only if absent; **never** print or upload its actual API key.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d --build
docker compose ps -a
docker compose logs pipeline --tail 40
```

The pipeline is an intentional one-shot job. `Exited (0)` is success. Fuseki and access-layer should stay running. If the pipeline fails, examine SHACL report and container logs before continuing.

## 3. Reproduce raw -> SQL -> RDF -> SHACL -> VoID

```powershell
docker compose run --rm --no-deps pipeline sh -c 'python data/prepare_option_a.py && python profiling/profiling.py && python data/build_example_sql.py'
docker compose run --rm --no-deps pipeline python pipeline/run.py --no-load
```

Observed: 2,925 prepared OFF; 797 USDA; 4,264 declared allergen link rows; 56,474 RDF triples; 0 SHACL violations / warnings; 94 VoID triples. Inspect `build/graph.nt`, `build/shacl-report.txt`, `build/void.ttl`. To reload the endpoint through the full one-shot pipeline, run `docker compose up -d --force-recreate pipeline` and inspect logs. Changes to graph storage should be made carefully: preserve existing Fuseki data for the demo.

## 4. Query Fuseki

Go to http://127.0.0.1:3030, select `kr`, then Query. Check total products with:

```sparql
PREFIX fs: <https://ul.edu.lb/kr/foodsafe#>
SELECT (COUNT(DISTINCT ?p) AS ?n)
WHERE { ?p a fs:PackagedProduct . }
```

Expected `n=3722`. Check OFF-to-USDA exact barcode overlaps:

```sparql
PREFIX fs: <https://ul.edu.lb/kr/foodsafe#>
SELECT (COUNT(DISTINCT ?off) AS ?n)
WHERE { ?off fs:fromSource fs:SourceOFF ; fs:sameProductAs ?usda . ?usda fs:fromSource fs:SourceUSDA . }
```

Expected `n=146`; the RDF also stores reverse links, so a raw directed-triple count may show 292.

## 5. Persistent ML dependencies and tests

The pipeline Dockerfile used for the seven-test Windows verification included:

```dockerfile
FROM python:3.12-slim
WORKDIR /work
COPY pipeline/requirements-pipeline.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir numpy scikit-learn pytest \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
CMD ["python", "pipeline/run.py"]
```

To rebuild and test:

```powershell
docker compose build pipeline
docker compose run --rm --no-deps pipeline python -m pytest -q tests/
```

**Windows observed result:** `7 passed, 2 warnings in 97.22s`; the warnings were `rdflib` N-Triples UTF-8 serializer notices, not failures. Before installing torch inside the permanent image, the run had `6 passed, 1 skipped`.

## 6. Run the unchanged learning experiments

```powershell
docker compose run --rm --no-deps pipeline python model/build_graph.py
docker compose run --rm --no-deps pipeline python model/baseline.py
docker compose run --rm --no-deps pipeline python model/gnn.py
docker compose run --rm --no-deps pipeline python model/link_prediction.py
```

Outputs: `model/outputs/foodsafe-graph.pt` (gitignored), `baseline.csv`, `gnn.csv`, `link-prediction.csv`.

Node-classification labels: 758 A/B, 1,187 C/D/E, 1,777 unlabelled (`-1`). Brand-disjoint seeds 11,23,37. Mean Macro-F1 0.5062 baseline / 0.5069 GNN; no meaningful improvement. The GNN's message passing uses same-brand relationships, not the OFF/USDA links. All data are synthetic.

## 7. Question-answering (offline vs live)

```powershell
docker compose exec -T access-layer python ask.py "How many OFF products are linked to a USDA product via sameProductAs?"
docker compose exec -T access-layer python evaluate.py --setting schema
```

Expected matched count `146`. `LLM_MODE=offline` is scripted output; it must not be reported as a live LLM benchmark. To use **real** Gemini, save `LLM_MODE=live` and `GOOGLE_API_KEY` into private `.env` and run:

```powershell
docker compose up -d --no-deps --force-recreate access-layer
```

Avoid showing the key in screen captures, logs or shared documents. Live result observed after correcting the ontology individual spelling in the prompt: five answerable questions F1=1.000, one correct refusal. This is a six-question micro-suite, with targeted improvements and no live repair triggered. A simulated repair flow did require two attempts and retrieved 16 brands after correction.

### Important prompt consistency check

The original `access-layer/prompt_rules.txt` contained an **obsolete** sentence saying the old sample had zero USDA records. That is false for Option A and must be removed/replaced in your local working copy. Use the included safe `FIX_STALE_PROMPT_RULE.ps1` file; it keeps all other prompt and validator changes.

## 8. Optional research checks not yet completed

- Full independent Morph-KGC R2RML output parity.
- Protégé OWL reasoner consistency on the complete prepared graph.
- External validation of identity matching and allergen labels against real products.
- A larger held-out and non-targeted question-answering evaluation.

Do not represent these checks as passed unless you actually run them.

## 9. Before sharing or GitHub

Review `README.md`, `report/REPORT.md`, `TEST_STATUS.md`, `FINAL_PREUPLOAD_CHECKLIST.md`. Check that no `.env`, `.bak`, private keys or caches are included. **Nothing in this docs update initializes Git or pushes to GitHub.**
