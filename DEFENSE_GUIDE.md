# SAFE-FOOD - 6-minute defense outline

**Minute 1: Problem.** Crowd-sourced product labels sometimes omit ingredient/allergen annotations. This is a knowledge quality question, not a medical risk recommendation.

**Minute 2: Ontology.** Show FoodOn identifiers plus `foodsafe:PackagedProduct`, declared allergen vs may-contain, and `hasLabelGapFlag`. OWL operates under the open-world assumption; missing graph facts are not automatically false.

**Minute 3: Quality and provenance.** Run SHACL on the good 50-product sample. Explain 48 salt measurements present, including 24 numerical zeros; 2 missing. Insert invalid barcode/energy and show the gate preventing load. Review flags=3 are not confirmed violations.

**Minute 4: Data integration.** Show raw CSV -> SQLite relational tables -> Python RDF -> SHACL -> VoID -> Fuseki. Point to R2RML file; explicitly state that actual R2RML engine equivalence is not verified and USDA is absent in this real-data snapshot.

**Minute 5: Learning.** Explain reported Nutri-Score A/B versus C/D/E, 47 labels, 3 seeds, held-out brands, train-only preprocessing, no target property/edge leakage. Compare honest mean macro F1; state small sample and one class/category limit. Product-allergen link prediction has a separate simple baseline.

**Minute 6: Access and refusal.** Answer one question in English using TEXT2SPARQL, then refuse a medical dose question. The offline mode demonstrates a deterministic contract, NOT a genuine Gemini quality score. For full LLM grading, rerun Live evaluation with a key.

Questions the professor may ask:
- **Why SHACL instead of OWL for mandatory barcodes?** SHACL is closed-world constraint validation; OWL reasoning does not equate missing assertions with violations.
- **Does zero salt mean unknown?** No, literal zero is an observed value, while null is missing. The RDFLib `any()` test previously hid zeros and was fixed in counts.
- **Why not predict label gaps with the GNN?** Only 3 positives in 50; cannot evaluate credibly. A Nutri-Score proxy task offers more balanced labels but is still limited.
- **Does F1=1 offline mean Gemini is perfect?** No; queries are fixed, so it proves implementation plumbing only.
- **What's the open research problem?** Multilingual ingredient parsing/ontology alignment with high precision and human review.
