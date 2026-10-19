# Entity resolution (Option A)

Exact equality of the synthetic identifiers in prepared CSVs yields 146 shared barcodes. Both OFF and USDA records remain distinct IRIs linked by foodsafe:sameProductAs. RDF asserts links in both directions.

Join location: in SQL/R2RML (`mapping/mapping.ttl`, last two TriplesMaps) and in Python RDF materialization (`mapping/materialize.py`); `er/match_products.py` prints the SQL exact-code join count. `data/quality/same_barcode_pairs.csv` is the human-readable audit with nutritional difference candidates.

No independent real-world matching accuracy can be inferred: overlap was planted in the synthetic generator. A matching barcode alone is not proof of real-world equivalent product versions.
