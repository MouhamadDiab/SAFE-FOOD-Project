# Option A data lineage

Raw user-supplied originals are under `data/raw/` (3,001 OFF-shaped rows; 800 USDA-shaped rows). They are synthetic fixtures created by an educational generator with seeded errors and identity overlap. **They were not fetched from the live OFF or USDA services.**

`python data/prepare_option_a.py` regenerates `data/sample/off_products.csv` and `data/sample/usda_products.csv`. It preserves all valid field values, strips identifier/name whitespace, removes duplicates (first occurrence retained) and excludes invalid identity and numeric values that cannot be fed to the production-style SHACL gate. Invalid `Z` Nutri-Score grades and invalid NOVA codes are set to **missing**, never guessed. A missing optional nutrient remains missing, and brand text stays unchanged.

The audit files under `data/quality/` include: `summary.json` with SHA256 checksums, `cleaning_actions.csv` with each removal or nulling, and `same_barcode_pairs.csv` with potential exact code matches plus energy-delta review candidates. **These are synthetic demonstration joins, not confirmed real-world identity matches.**

The fields `source=openfoodfacts` and `source=usda_fdc` are inherited from the teaching generator and represent **the intended schema**. They do **not** prove external provenance. Likewise, original `retrieved_date` values come from the synthetic fixture, not independently verified retrieval events.

`data/build_example_sql.py` converts prepared samples into tables and normalized allergen relations. `data/fetch_or_build_sample.py` is the legacy synthetic generator and is intentionally not part of normal Option A reproduction.
