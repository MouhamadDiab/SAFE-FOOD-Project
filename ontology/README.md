# Ontology layer - SAFE-FOOD Option A

- `foodsafe.ttl`: application ontology for `PackagedProduct`, `Allergen`, `NutriScoreGrade`, `DataSource`, `LabelIncomplete`, `LabelOpaque`; declared relations `hasDeclaredAllergen`, `mayContainAllergen`, `hasNutriScore`, `fromSource`, `sameProductAs` (symmetric); data-valued fields `barcode`, `productName`, `energyKcal100g`, `fat100g`, `sugars100g`, `proteins100g`, `salt100g`, `retrievedOn`, `hasLabelGapFlag`.
- `foodon-slim.ttl`: educational subset of FoodOn identifiers, with a broad food product superclass.
- `ontology.ttl`: entry-point explanatory file, not a third full ontology.
- `shapes/shapes.ttl`: separate SHACL constraints **not** an ontology; R2RML mapping also separate.

The graph's `SourceOFF` and `SourceUSDA` denote **source-shaped fixture groupings**, not proof of a retrieval from those external databases. This Option A cohort is intentionally synthetic. Open both ontology TTL files in Protégé; inspect subclasses/properties and run HermiT or ELK separately on the user's machine. Ontology parse checks are not equivalent to reasoner consistency testing.
