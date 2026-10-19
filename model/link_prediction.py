"""Small, exploratory product-allergen link ranking. No false GNN claim.

For each seed, hide 20% of product-allergen edges and predict their
allergen type using (a) global popularity or (b) neighbor brand incidence.
Brand heuristic uses other products' training links only; no test link used.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv
import numpy as np
import torch
OUT=Path(__file__).resolve().parent/'outputs'


def main():
    data=torch.load(OUT/'foodsafe-graph.pt',map_location='cpu',weights_only=False)
    links=list(map(tuple,data['edge_product_allergen'].T.tolist()))
    n_a=len(data['allergen_iris']);brands=data['brand_of']
    if n_a<2 or len(links)<5:
        raise ValueError('Too few allergen classes or links for exploratory ranking')
    rows=[]
    for seed in (11,23,37):
        rng=np.random.default_rng(seed);order=rng.permutation(len(links))
        ntest=max(1,round(.2*len(links)))
        test=[links[i] for i in order[:ntest]];train=[links[i] for i in order[ntest:]]
        pop=Counter(a for p,a in train)
        bybrand=defaultdict(Counter)
        for p,a in train:bybrand[brands[p]][a]+=1
        def rank(p,correct,use_brand):
            scores={a: (bybrand[brands[p]][a] if use_brand else 0) for a in range(n_a)}
            if use_brand and not any(scores.values()):scores={a:pop[a] for a in range(n_a)}
            if not use_brand:scores={a:pop[a] for a in range(n_a)}
            order=sorted(range(n_a),key=lambda a:(-scores[a],a))
            return order.index(correct)+1
        for method,use_brand in [('popularity',False),('brand_neighbors',True)]:
            ranks=[rank(p,a,use_brand) for p,a in test]
            row={'seed':seed,'method':method,'test_edges':len(test),'allergen_classes':n_a,
                 'mrr':round(float(np.mean([1/r for r in ranks])),4),
                 'hits_at_1':round(float(np.mean([r==1 for r in ranks])),4),
                 'hits_at_3':round(float(np.mean([r<=3 for r in ranks])),4)}
            print('link-prediction',row);rows.append(row)
    with (OUT/'link-prediction.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Saved',OUT/'link-prediction.csv')

if __name__=='__main__':main()
