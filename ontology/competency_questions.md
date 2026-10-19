# Competency questions (SAFE-FOOD)

Each CQ must be answerable from the graph (SPARQL) after mapping. Axioms and properties exist *because* of these questions.

| ID | Question | Needs |
|---|---|---|
| CQ1 | Which products declare the milk allergen? | `foodsafe:hasDeclaredAllergen`, allergen individuals |
| CQ2 | Which products mention milk (or wheat, egg, …) in ingredients text but lack the matching allergen tag? | `foodsafe:labelIncomplete` / ingredients + allergens |
| CQ3 | Which products are typed under a FoodOn food class (via category mapping)? | FoodOn reuse / `rdfs:subClassOf` |
| CQ4 | Which OFF and USDA records refer to the same barcode (same product candidate)? | `foodsafe:sameProductAs` or shared IRI |
| CQ5 | Which products miss Nutri-Score but have fat and protein values? | `foodsafe:hasNutriScore`, nutrition properties |
| CQ6 | Which products are label-opaque (no allergens and no ingredients text)? | `foodsafe:LabelOpaque` |
| CQ7 | What is the provenance (source system + date) of a product fact? | `foodsafe:fromSource`, `foodsafe:retrievedOn` |

## SPARQL sketches (prefixes)

```sparql
PREFIX foodsafe: <https://ul.edu.lb/kr/foodsafe#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# CQ1
SELECT ?p ?name WHERE {
  ?p a foodsafe:PackagedProduct ;
     foodsafe:hasDeclaredAllergen foodsafe:AllergenMilk ;
     foodsafe:productName ?name .
}
```
