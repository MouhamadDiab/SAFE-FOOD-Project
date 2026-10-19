# Option A R2RML and RDF mapping

From `data/example.sql` the pipeline creates `build/example.sqlite`. `mapping/materialize.py` (Python + RDFLib) materializes the RDF for execution; `mapping/mapping.ttl` is a declarative R2RML equivalent to test with Morph-KGC independently.

- OFF and USDA records use distinct IRIs even when they have the same (synthetic) barcode.
- Both `off_products` and `usda_products` map to `foodsafe:PackagedProduct`.
- `foodsafe:sameProductAs` is emitted **in both directions** for each exact equal barcode (146 pairs -> 292 directed statements) in the Python implementation. A reverse R2RML TriplesMap was added for the same intended semantics.
- OFF includes declared allergens, possible traces, regex-based review flags and reported grades; USDA-shaped fixtures contain no Nutri-Score grades.
- The mapper intentionally does not silently clean bad data: SHACL must catch invalid required fields and numeric bounds. The *separate* preparation step filters invalid raw records transparently.

Local Python generated 56,474 triples. Morph-KGC parity on **this new Option A snapshot** is not verified; run `mapping/verify_r2rml.py` with Morph-KGC and SQLAlchemy installed before claiming identical graphs.
