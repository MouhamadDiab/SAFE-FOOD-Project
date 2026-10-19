# SAFE-FOOD / Option A - verified technical report

**Date:** 20 October 2026
**Course:** MSc Knowledge Representation
**Authors / team roles:** [Add confirmed details before submission]
**Data disclosure:** All OFF-shaped and USDA-shaped product rows are deliberately **synthetic educational data**. No claim is made that any listed product, barcode link, nutrient label or allergen declaration was verified in the real world.

## Abstract

SAFE-FOOD evaluates a teaching architecture for representing and querying heterogeneous packaged-food records via SQLite, RDF/OWL semantics, SHACL quality constraints, bilateral barcode joins, and Apache Jena Fuseki. An English-to-SPARQL access layer uses a controlled offline mode and an opt-in Gemini live model. A separate, unchanged GraphSAGE-style GNN and logistic baseline classify reported synthetic Nutri-Score A/B versus C/D/E groups; their near-identical scores do not support a meaningful graph-learning advantage. Windows Docker execution confirmed 56,474 RDF triples, 3,722 products, 146 planted cross-source matched pairs, zero SHACL violations/warnings and seven passing project tests. A small, partly targeted live Gemini micro-evaluation reached F1 1.000 across five answerable questions and one correct refusal. These figures establish a functional demonstration, not generalizable food-safety or source-integration accuracy.

## 1. Research question and scope

Can a deliberately heterogeneous, two-source-shaped package-food dataset be integrated and validated into an ontology-based graph, queried through natural-language-generated SPARQL, and used as input for an unchanged graph-learning demonstration, while preserving provenance and documenting uncertainty?

This project does not classify actual allergen hazard, confirm labeling compliance, prescribe dietary or medical decisions, or prove real OFF-USDA identity links. The datasets are synthetic (controlled test fixtures).

## 2. Data preparation and provenance

The raw teaching files contain 3,001 OFF-shaped rows and 800 USDA-shaped rows, including intentional invalid values, duplicated product identifiers and shared barcode strings. The preparation script keeps original files and logs cleaning steps in `data/quality/`. Its prepared datasets contain 2,925 OFF and 797 USDA records. Some optional nutrition or label fields remain genuinely missing; they are not converted to zeros. The SQL materialization creates 4,264 declared allergen rows. Source-specific product identity is retained in RDF so the two sides of a candidate barcode match remain distinguishable.

Exactly 146 distinct exact-barcode matched pairs connect the sources after cleaning; symmetric statements yield 292 directional `sameProductAs` triples. They are not manually validated commercial matches. Their creation does not merge unequal nutritional data.

## 3. Ontology, mapping and validation

`ontology/foodsafe.ttl` defines an application vocabulary (such as `PackagedProduct`, `hasDeclaredAllergen`, `hasNutriScore`, `fromSource`, `sameProductAs`), with `ontology/foodon-slim.ttl` giving a limited selection of FoodOn identifiers rather than the full ontology. `mapping/materialize.py` executes RDF generation, and `mapping/mapping.ttl` records a declarative R2RML mapping. The observed prepared graph has **56,474 RDF triples**, **3,722 typed packaged products** and 94 VoID metadata triples.

The pipeline's pySHACL stage reports **0 violations and 0 warnings** for the prepared data under the installed shapes. This is not evidence that every source fact is true or that no important validation rule is missing. `shapes/shapes.ttl` enforces named/identifier presence and selected numeric bounds. Rules comparing ingredients and declared allergen tags create review flags, not confirmed noncompliance findings.

## 4. Fuseki SPARQL and bilingual-source integration

Apache Jena Fuseki hosts the prepared graph at dataset `kr`. SPARQL successfully counted 3,722 products and 146 distinct OFF product nodes linked to USDA nodes through `sameProductAs`. A join also displayed paired source-specific records and their optional attribute values. SPARQL treats unknown RDF individuals syntactically as legal IRIs, so a mistyped allergen URI can return an empty result instead of raising a parse error.

A practical example exposed `AllergenPeanut` vs the actual `AllergenPeanuts` individual. The corrected URI yielded 16 distinct brand names associated with 333 peanut-allergen declarations in the synthetic graph. This motivated a targeted prompt rule and an `unknown_allergen_individuals` validator.

## 5. Learning experiment (source code unchanged)

The GNN consumes five per-100g nutrition features: energy, fat, sugars, protein and salt. It aggregates **same-brand neighbor** features using a one-hop GraphSAGE-style mean operation. It does **not** message-pass over `sameProductAs` or product-allergen edges. The binary task labels 758 OFF nodes as class 1 (Nutri-Score A/B), 1,187 as class 0 (C/D/E), and leaves 1,777 nodes unlabelled. Train-only median imputation and scaling avoid test-set leakage; splits are brand-disjoint across seeds 11, 23 and 37. The original model task and architecture were not changed in the walkthrough.

| Seed | Logistic baseline Macro-F1 | GNN Macro-F1 |
| --- | ---: | ---: |
| 11 | 0.5062 | 0.5211 |
| 23 | 0.4830 | 0.4957 |
| 37 | 0.5293 | 0.5038 |
| **Mean** | **0.5062** | **0.5069** |

The average gap is ~0.0007. This is not a meaningful improvement, and synthetic labels have weak realistic nutritional meaning. Separate product-allergen link ranking methods produced mean MRR approximately 0.2573 (popularity) and 0.2519 (brand neighbors), demonstrating no benefit of the latter on this sample. These are heuristic link-ranking results, not a neural allergen predictor.

## 6. Live natural-language access and validation

An access layer generates SPARQL for Fuseki; `LLM_MODE=offline` is a deterministic example implementation, not a true Gemini evaluation. With `LLM_MODE=live` and a privately configured Google API key, live SPARQL generation correctly answered the 146-pair count question.

Before targeting the allergen individual-name issue, a six-question live evaluation produced schema mean F1 0.800 and examples/repair 0.688. The final schema-only rerun after adding exact-IRI guidance and name validation yielded **F1 1.000 across five answerable questions**, plus **one correct refusal** for a medical-advice question. Five answers were correct in that one run. Results are sensitive to prompt wording and a very small, partly targeted evaluation sample. The updated `examples`/`repair` settings were **not** separately rerun, and no real live auto-repair was exercised in that final evaluation.

A controlled mock-model test deliberately returned an invalid allergen IRI on the first call. The validator flagged it, injected feedback into a second simulated model call, and successfully executed a corrected query returning 16 brands. That proves the program's two-attempt control-flow behavior for that mock case, not general LLM repair reliability.

## 7. Testing, reproducibility and known gaps

Windows Linux-Docker runs successfully built the pipeline, verified the SHACL gate and Fuseki integration, saved the baseline/GNN/link-ranking CSV outputs, and eventually executed **7/7 tests** after persisting PyTorch CPU and scikit-learn dependencies into the pipeline image. The two `rdflib` UTF-8 warnings are non-fatal serializer notices.

Still not independently verified here: complete Morph-KGC to Python materialization parity; OWL reasoning consistency through Protégé on the final graph; generalization on real OFF and USDA product records; robust held-out language-model QA on a larger unbiased set; reproducibility on a completely unrelated machine. The old Option A PDF draft predates these Windows checks, so this report supersedes its pending-verification paragraphs.

## 8. Conclusion

SAFE-FOOD demonstrates a functioning synthetic two-source RDF integration and question-answering pipeline, with explicit provenance, typed semantics, zero SHACL violations on the prepared graph and working automated tests. The GNN provides an educational comparison rather than an evidence-based nutritional classifier. Stronger scientific claims require real independently verified data, larger evaluation sets and careful data-source identity checks.
