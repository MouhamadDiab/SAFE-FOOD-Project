# Source provenance and licences

- **Open Food Facts**: 50 product entries originally queried via the official API and enriched by product barcode on 2026-10-19. Source: https://world.openfoodfacts.org/ . Database licence: Open Database License 1.0 (ODbL). Include the attribution "Contains data from Open Food Facts". Preserve database share-alike as applicable. Values are crowd-sourced, not independently authenticated label readings.
- **FoodOn**: the FoodOn identifier subset in `ontology/foodon-slim.ttl` is attributed to FoodOn and contributors (CC BY 4.0), https://foodon.org/ and https://github.com/FoodOntology/foodon . This repository uses a slim local sketch with selected identifiers; it is not a copy of the complete, current FoodOn release.
- **USDA FoodData Central**: the empty table is a future integration hook, not an active product data source in this build. https://fdc.nal.usda.gov/

The legacy `data/fetch_or_build_sample.py` can generate **synthetic** teaching fixtures; they are not real OFF or USDA observations.
