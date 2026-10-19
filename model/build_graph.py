"""Construct a reproducible small learning graph from the validated RDF output.

Targets are reported Nutri-Score (A/B vs C/D/E), not inferred product safety.
Label-gap positives are retained for graph queries but are TOO FEW to train on.
"""
from __future__ import annotations

from pathlib import Path
import math
import torch
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'model/outputs'
FS = Namespace('https://ul.edu.lb/kr/foodsafe#')
FEATURES = (FS.energyKcal100g, FS.fat100g, FS.sugars100g, FS.proteins100g, FS.salt100g)


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    g = Graph().parse(ROOT / 'build/graph.nt', format='nt')
    products = sorted(set(g.subjects(RDF.type, FS.PackagedProduct)), key=str)
    brands = []
    flags = []
    grades = []
    features = []
    for p in products:
        brand = next(g.objects(p, FS.brandName), None)
        brands.append(str(brand).strip().lower() if brand is not None else f'unknown-{p}')
        gap = next(g.objects(p, FS.hasLabelGapFlag), None)
        flags.append(int(gap is not None and str(gap).lower() in ('true', '1')))
        grade = next(g.objects(p, FS.hasNutriScore), None)
        letter = str(grade).rsplit('#', 1)[-1]
        grades.append(1 if letter in ('GradeA','GradeB') else 0 if letter in ('GradeC','GradeD','GradeE') else -1)
        row = []
        for pred in FEATURES:
            term = next(g.objects(p, pred), None)
            row.append(float(term) if term is not None else float('nan'))
        features.append(row)
    assert len(products) == len(set(products))
    allergen_ids = sorted({a for p in products for a in g.objects(p, FS.hasDeclaredAllergen)}, key=str)
    a_index = {u: i for i, u in enumerate(allergen_ids)}
    edges = [(i, a_index[a]) for i, p in enumerate(products) for a in g.objects(p, FS.hasDeclaredAllergen)]
    # Brand-neighbor links. No label-bearing allergen edges feed node classification.
    from collections import defaultdict
    groups = defaultdict(list)
    for i, b in enumerate(brands): groups[b].append(i)
    src, dst = [], []
    for ids in groups.values():
        if len(ids) > 1:
            for a, b in zip(ids, ids[1:] + ids[:1]):
                if a != b:
                    src += [a,b]
                    dst += [b,a]
    data = {
        'product_iris': [str(p) for p in products],
        'allergen_iris': [str(a) for a in allergen_ids],
        'x_product': torch.tensor(features, dtype=torch.float32),
        'y_nutriscore_bin': torch.tensor(grades, dtype=torch.int64),
        'y_label_gap': torch.tensor(flags, dtype=torch.int64),
        'brand_of': brands,
        'edge_brand_neighbor': torch.tensor([src,dst],dtype=torch.long) if src else torch.zeros(2,0,dtype=torch.long),
        'edge_product_allergen': torch.tensor(edges,dtype=torch.long).T.contiguous() if edges else torch.zeros(2,0,dtype=torch.long),
    }
    out=OUT/'foodsafe-graph.pt'
    torch.save(data,out)
    from collections import Counter
    print(f'Graph learning data: {len(products)} products, {len(allergen_ids)} allergen types, {len(edges)} declared links')
    print('Nutri-Score labels:',dict(Counter(grades)), 'label-gap flags:',sum(flags))
    print('Saved',out)

if __name__ == '__main__': main()
