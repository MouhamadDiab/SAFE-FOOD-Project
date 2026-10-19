# SAFE-FOOD - before publishing on GitHub

**Current status:** Preparation and local verification in progress. Do not initialize, connect or push a repository until every relevant box below is reviewed.

- [x] Raw synthetic data and prepared data exist; disclosed as **synthetic**.
- [x] RDF and SHACL pipeline run on Windows Docker: 56,474 triples, 0 violations.
- [x] Fuseki SPARQL: 3,722 products; 146 synthetic identity pairs.
- [x] Baseline, GNN, link-ranking results saved; unchanged model architecture and task.
- [x] Tests: 7 passed, 0 skipped, 2 non-fatal serializer warnings.
- [x] Live Gemini schema evaluation after prompt update; small 6-question sample only.
- [x] Synthetic two-attempt repair-loop test passed.
- [ ] Make sure `access-layer/prompt_rules.txt` no longer says USDA has zero records.
- [ ] Ensure local `access_layer.py` still includes `unknown_allergen_individuals` validation.
- [ ] Keep final ML-ready `pipeline/Dockerfile` and re-verify after any changes.
- [ ] Verify `.env` is excluded; do not commit secret backups, shell histories, caches, tokens or files containing keys.
- [ ] Inspect `git status --short` and `git diff --cached --name-only` **after** initializing the new repository.
- [ ] Confirm teammates' names, contributions and instructor-required submission format.
- [ ] Decide whether the older outdated PDF draft should be archived, not shown as final.
- [ ] Optionally evaluate more unseen QA questions to qualify the targeted Gemini F1 metric.
- [ ] Confirm the desired GitHub destination. **No push now.**

## Secret audit (before any Git command that stages files)

The `.gitignore` excludes `.env`, `.env.*` except `.env.example`, `build/`, temporary caches and `model/outputs/*.pt`. Secrets must be protected even if a file is manually force-added or was committed in another repository earlier. Do not copy `.env` into documentation or screenshots. Never paste a real API key into ChatGPT, a commit message or public issue. If a key is exposed, revoke/rotate it at Google AI Studio.

The older `SAFE-FOOD-REVIEWED` GitHub repository is independent of `SAFE-FOOD-OPTION-A-READY`. Do not force-push or overwrite that repository unless the team explicitly chooses it.
