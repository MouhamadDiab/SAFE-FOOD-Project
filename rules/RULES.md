# Constraints - small real-data scope

R01/R03 require identity and names. R10/R12 bound nutrition data *when present*; nutrition missingness is not equivalent to zero. R13 requires recorded Nutri-Score to point to a known grade. These are enforced with SHACL (`shapes/shapes.ttl`) and the default pipeline is not permitted to silently discard bad rows.

R17 is a heuristic text mismatch between ingredients and declared allergen tags in a crowd-sourced feed; it is intentionally a **review flag, not a Violation or a judgement about food safety**. Because tagging is multilingual, absence of a tag alone cannot imply absence of allergen in food or packaging.

The R17 detector is `data/build_example_sql.py:label_gap`. The warning examples in `shapes/warnings.ttl` are not applied to the default CI gate. Warning and Violation counts must state which shapes were evaluated.
