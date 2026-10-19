"""GraphSAGE-style mean aggregation on brand-neighbor edges, CPU-only.

Important: node target is a *reported Nutri-Score grade* (A/B vs C/D/E),
not a medical safety label. Neighbor-aggregate input uses no label edges.
"""
from pathlib import Path
import csv
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from common import SEEDS,group_split,preprocess,metrics
OUT=Path(__file__).resolve().parent/'outputs'


class SageLike(nn.Module):
    def __init__(self,in_dim,hidden=24):
        super().__init__()
        self.lin_self=nn.Linear(in_dim,hidden)
        self.lin_msg=nn.Linear(in_dim,hidden)
        self.out=nn.Linear(hidden,2)

    def forward(self,x,edge_index):
        if edge_index.numel()==0:
            return self.out(F.relu(self.lin_self(x)))
        src,dst=edge_index
        neighbor_sum=torch.zeros_like(x)
        neighbor_sum.index_add_(0,dst,x[src])
        deg=torch.bincount(dst,minlength=x.shape[0]).to(x.dtype).unsqueeze(1)
        mean=neighbor_sum/deg.clamp(min=1)
        return self.out(F.relu(self.lin_self(x)+self.lin_msg(mean)))


def main():
    torch.set_num_threads(1)
    data=torch.load(OUT/'foodsafe-graph.pt',map_location='cpu',weights_only=False)
    y=data['y_nutriscore_bin']
    edges=data['edge_brand_neighbor']
    rows=[]
    for seed in SEEDS:
        tr,te=group_split(data,seed)
        x=torch.tensor(preprocess(data,tr),dtype=torch.float32)
        torch.manual_seed(seed)
        model=SageLike(x.shape[1]);opt=torch.optim.Adam(model.parameters(),lr=.015,weight_decay=1e-3)
        for epoch in range(100):
            model.train();opt.zero_grad()
            loss=F.cross_entropy(model(x,edges)[tr],y[tr]);loss.backward();opt.step()
        model.eval()
        with torch.no_grad():
            p=F.softmax(model(x,edges)[te],dim=1)[:,1].cpu().numpy()
        row={'seed':seed,'train_n':len(tr),**metrics(y[te].cpu().numpy(),p)}
        rows.append(row);print('graphsage-style',row)
    with (OUT/'gnn.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Saved',OUT/'gnn.csv')

if __name__=='__main__':main()
