# SQLite -> RDF integration

`mapping/mapping.ttl` declares an R2RML design for the OFF tables, allergens, traces, label-gap flag, recorded Nutri-Score, nutrition, source metadata, and optional USDA table. `mapping/materialize.py` is the **Python implementation actually executed and tested** by `pipeline/run.py`. It retains malformed source rows so that violations reach the SHACL gate; it does not silently clean records in order to pass validation.

In this self-contained version, `data/sample/usda_products.csv` holds headers only and `data/example.sql` has 0 USDA rows. It would be misleading to claim an OFF-USDA linkage experiment. Running a genuine Morph-KGC R2RML engine and verifying exact parity with the Python graph are **not yet completed**. Do not mark that as tested.
