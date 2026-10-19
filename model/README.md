# Graph learning: same model, Option A data

**No edits to `model/gnn.py`, `model/baseline.py`, `model/common.py`, `model/build_graph.py` or `model/link_prediction.py`.** Compare SHA256 with the pre-Option-A project if needed.

Prediction target: `1 = Nutri-Score A/B`, `0 = Nutri-Score C/D/E`. All other nodes get label -1 and are excluded from classifier losses/metrics; these may still participate in the brand-neighbor graph. The label is a *synthetic reported grade*, not a safety determination or independent true label.

Inputs: energy (kcal/100g), fat, sugars, protein and salt (g/100g). For each seed 11/23/37: brand-disjoint group split on labelled nodes; training-only median imputation and standard scaling. Baseline: class-balanced Logistic Regression; GraphSAGE-style model: one-hop mean neighbor features on brand edges, 100 epochs, two logits, cross-entropy. Other RDF edges including `sameProductAs` are not used by this particular GNN.

The dataset has 3,722 total nodes; 1,945 valid labelled nodes. Three-seed mean Macro-F1 baseline 0.506; GNN 0.507 (tiny, not a substantive improvement). Scores are exploratory because grade labels were generated without a realistic Nutri-Score formula.

`model/link_prediction.py` is a separate heuristic ranking experiment on product-allergen edges (popularity vs brand-neighbor frequency), NOT a neural GNN.

Run after pipeline: `python model/build_graph.py; python model/baseline.py; python model/gnn.py; python model/link_prediction.py`.
