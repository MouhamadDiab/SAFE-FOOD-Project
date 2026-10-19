"""Baseline: grouped-by-brand LogisticRegression for reported Nutri-Score A/B."""
from pathlib import Path
import csv
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from common import SEEDS,group_split,preprocess,metrics
OUT=Path(__file__).resolve().parent/'outputs'


def main():
    data=torch.load(OUT/'foodsafe-graph.pt',map_location='cpu',weights_only=False)
    y=data['y_nutriscore_bin'].numpy()
    rows=[]
    for seed in SEEDS:
        tr,te=group_split(data,seed)
        x=preprocess(data,tr)
        clf=LogisticRegression(max_iter=2000,class_weight='balanced',random_state=seed)
        clf.fit(x[tr],y[tr])
        p=clf.predict_proba(x[te])[:,1]
        row={'seed':seed,'train_n':len(tr),**metrics(y[te],p)}
        rows.append(row)
        print('baseline',row)
    with (OUT/'baseline.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Saved',OUT/'baseline.csv')

if __name__=='__main__': main()
