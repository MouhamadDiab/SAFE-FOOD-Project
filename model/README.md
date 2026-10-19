# Learning layer - scoped to 50 real products

Two tasks with explicit limitations:

1. **Node classification:** predict the *reported* Nutri-Score A/B (1) vs C/D/E (0). Unreported grades are excluded from evaluation. It is not a clinical health/safety prediction and not necessarily a generalizable scientific model. Nutrition features are standardized and imputed **on train brands only**, same splits for LogisticRegression and GraphSAGE-style one-hop mean message passing. Three seeds (11,23,37); brand-disjoint holdouts. Graph edges are only between products with the same brand. The target is NOT in the input graph features or its edges.
2. **Link prediction demonstration:** rank a hidden product-allergen edge among observed allergen types using global popularity vs frequency of links in the product's brand's neighboring products. This is *heuristic graph-aware link ranking*, NOT a neural link predictor. Three seeds; 20% of links held out. With just a few observed allergen types these scores are unstable.

`y_label_gap` is retained, but with 3 positives among 50 nodes the study does **not** fit a label-gap classifier. Those three records are candidates for human review, not verified packaging violations.

```
python model/build_graph.py
python model/baseline.py
python model/gnn.py
python model/link_prediction.py
```

Outputs are under `model/outputs/*.csv`. Scores must be recomputed if the data changes.
