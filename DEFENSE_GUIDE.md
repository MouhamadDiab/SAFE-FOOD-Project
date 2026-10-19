# SAFE-FOOD Option A - Defense cheat sheet

**Project question:** Can a reproducible ontology-based pipeline integrate two *synthetic source-shaped* food datasets, validate constraints and answer semantic queries, while an unchanged brand-neighbor GNN performs exploratory Nutri-Score classification?

**Q: Are these real USDA and OFF records?** No. The two original CSVs are synthetic teaching fixtures generated to resemble OFF and USDA schemas, with planted invalid values and deliberate barcode overlaps. This is a proof of integration architecture, NOT demonstrated real-world data integration.

**Q: Why two datasets?** To exercise heterogenous SQL tables, separate identifiers/source records, exact-code entity linking, provenance distinctions and queryable cross-source comparisons. There were 150 original synthetic shared codes and 146 retained prepared candidate pairs.

**Q: Which ontology is used?** `foodsafe.ttl` is the application vocabulary; `foodon-slim.ttl` reuses some FoodOn identifiers. SHACL constraints live in `shapes/`, R2RML in `mapping/`. Protégé reasoner checking is pending.

**Q: Where is the JOIN?** SQL `off_products.code = usda_products.gtin_upc` in both R2RML link TriplesMaps and Python RDF materializer. The two product individuals remain separate, joined by symmetric `sameProductAs` links. Equal synthetic codes are *candidate* identities, not independent real-world verification.

**Q: Why SHACL?** OWL describes semantic classes/properties; SHACL is a closed-world check of required barcode/name and finite nutrient ranges. Invalid raw rows are preserved and documented; the prepared cohort excludes gate-breaking rows. Original source generator planted the errors.

**Q: What exactly does GNN learn?** Target y=1 for reported Nutri-Score A/B, y=0 for C/D/E. Inputs are energy, fat, sugar, protein and salt plus same-brand neighbor features. USDA records have no grades, are not training targets, but can influence neighbor aggregates; OFF-USDA `sameProductAs` is NOT a GNN edge. GNN code unmodified.

**Q: Does the GNN detect allergens or data errors?** No. Allergen-gap flags are separate rule-based review signals. `gnn.py` performs Nutri-Score classification, not medical safety assessment or quality-error correction.

**Q: Does the GNN outperform Logistic Regression?** Not meaningfully on synthetic data: mean Macro-F1 0.507 vs 0.506 over three seeds. Labels were generated approximately randomly, so external validity is minimal.

**Q: What remains before academic submission?** Run full pySHACL and Docker/Fuseki checks on Windows, independent Morph-KGC parity, complete Gemini evaluation if required, Protégé reasoning, team credits, and make synthetic limitations prominent in the report.

**Safe SHACL demonstration:** `python data/demo_bad_shacl.py` catches a planted negative-energy raw record in memory, without changing the prepared RDF or Fuseki.
