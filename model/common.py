"""Shared, leakage-aware splits and preprocessing for both classifiers."""
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, balanced_accuracy_score, average_precision_score

SEEDS=(11,23,37)


def group_split(data, seed):
    y=data['y_nutriscore_bin'].numpy()
    brands=np.array(data['brand_of'])
    ids=np.flatnonzero(y>=0)
    for offset in range(100):
        split=GroupShuffleSplit(n_splits=1,test_size=.25,random_state=seed+offset)
        tri,tei=next(split.split(ids,y[ids],groups=brands[ids]))
        tr,te=ids[tri],ids[tei]
        if len(np.unique(y[tr]))==2 and len(np.unique(y[te]))==2:
            assert not set(brands[tr]) & set(brands[te]), 'brand leakage'
            return tr,te
    raise ValueError('Cannot create binary-labelled brand-disjoint train/test sets')


def preprocess(data,tr):
    x=data['x_product'].numpy().astype(float)
    x[~np.isfinite(x)]=np.nan
    imputer=SimpleImputer(strategy='median',add_indicator=False)
    xtr=imputer.fit_transform(x[tr])
    xall=imputer.transform(x)
    scaler=StandardScaler().fit(xtr)
    return scaler.transform(xall).astype('float32')


def metrics(y_true,proba):
    pred=(proba>=.5).astype(int)
    return {
        'macro_f1': round(float(f1_score(y_true,pred,average='macro',zero_division=0)),4),
        'balanced_accuracy': round(float(balanced_accuracy_score(y_true,pred)),4),
        'average_precision': round(float(average_precision_score(y_true,proba)),4),
        'test_n':len(y_true), 'test_positive':int(sum(y_true))
    }
