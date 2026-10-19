# SHACL shapes (SAFE-FOOD)

`shapes.ttl` implements closed-world checks from `rules/constraint_inventory.csv`.

| Severity | Examples | Gate |
|---|---|---|
| Violation | missing barcode/name; impossible nutrients; bad Nutri-Score IRI | fails CI / pipeline |
| Warning | no allergens; label gap (R17); missing Nutri-Score with macros | passes, must triage |

Targeting: `sh:targetClass foodsafe:PackagedProduct` — always check focus-node counts before trusting a green run.
