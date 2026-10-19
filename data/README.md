# Data used in the simplified project

The **default source is 50 actual Open Food Facts yogurt entries**, collected and enriched 2026-10-19. The source CSV is `data/real_off_enriched.csv`; a copy at `data/sample/off_products.csv` is used to generate `data/example.sql`. No external API request is required for a clean build.

`data/sample/usda_products.csv` intentionally contains **headers only**. No synthetic OFF/USDA matches are passed off as observed real product matches. USDA integration and entity resolution remain a documented extension, not a demonstrated result.

CSV fields may be missing. In particular, salt is missing for two products, whereas a reported numeric zero is a valid value. The normalized allergen table `off_allergens` includes known allergen tags; raw `allergens_tags` can also contain unrecognized names, which are not silently interpreted as safety statements.

Run from repository root:

```
python data/build_example_sql.py
python pipeline/run.py --no-load
```

`data/fetch_or_build_sample.py` is **legacy synthetic teaching-data generation** and now refuses to overwrite the real data unless you explicitly pass `--allow-synthetic-overwrite`. Do not use this mode for the real-data submission. See `data/LICENCES.md` and `report/REPORT.md` for provenance and limitations.
