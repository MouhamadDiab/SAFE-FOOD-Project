# SAFE-FOOD Option A - start here

This is a **synthetic teaching project**, not a database of verified real products.

1. Open `SAFE-FOOD-OPTION-A-READY` in PowerShell; start Docker Desktop.
2. `if (!(Test-Path .env)) { Copy-Item .env.example .env }`
3. `docker compose up -d --build`
4. `docker compose ps -a` and `docker compose logs pipeline --tail 40`
5. Fuseki `http://127.0.0.1:3030`, dataset `kr`, expected 3,722 products / 146 OFF-USDA candidate pairs.
6. `docker compose run --rm --no-deps pipeline python -m pytest -q tests/` should yield **7 passed** with the ML-ready Docker image.
7. For the offline scripted demo or opt-in live Gemini, see `RUN_GUIDE_AR.md`.

Full metrics: `README.md`. Final results and caveats: `report/REPORT.md` / `report/SAFE_FOOD_Option_A_Final_Report.pdf`. No GitHub push has been performed in this update.
