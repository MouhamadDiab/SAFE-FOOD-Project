#!/usr/bin/env python3
"""Prepare Option A teaching CSVs deterministically without inventing labels.

Source originals: data/raw/{off_products_original,usda_products_original}.csv
Prepared outputs: data/sample/*.csv (same existing ETL schemas).
Audits: data/quality/*.csv, data/quality/summary.json.

Not external OFF/USDA records: synthetic, named after source-shaped schemas.
Never use these for claims about the real foods or clinical safety.
"""
from __future__ import annotations
import collections
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'; PREP=ROOT/'sample'; AUD=ROOT/'quality'
OFF=RAW/'off_products_original.csv'; USDA=RAW/'usda_products_original.csv'
FIELDS_NUMERIC_OFF = {
 'energy_kcal_100g':(0,900), 'fat_100g':(0,100),
 'saturated_fat_100g':(0,100), 'carbohydrates_100g':(0,100),
 'sugars_100g':(0,100), 'proteins_100g':(0,100),
 'salt_100g':(0,100), 'fiber_100g':(0,100),
}
FIELDS_NUMERIC_USDA={
 'energy_kcal_100g':(0,900),'fat_100g':(0,100),
 'sugars_100g':(0,100),'proteins_100g':(0,100),'salt_100g':(0,100),
}
VALID_GRADE=set('ABCDE')


def read(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        dr=csv.DictReader(f)
        if dr.fieldnames is None: raise ValueError('No columns in '+str(path))
        return dr.fieldnames,list(dr)


def write(path,cols,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='raise')
        w.writeheader();w.writerows(rows)


def check_numeric(record,bounds):
    errors=[]
    for col,(lo,hi) in bounds.items():
        x=(record.get(col) or '').strip()
        if not x: continue # preserve missing observations; model imputes using train data
        try: num=float(x)
        except ValueError:
            errors.append('invalid_'+col);continue
        if not math.isfinite(num) or not lo <= num <= hi:
            errors.append('out_of_range_'+col)
    return errors


def prepare(path,kind):
    cols,rows=read(path)
    codecol='code' if kind=='OFF' else 'gtin_upc'
    namecol='product_name' if kind=='OFF' else 'description'
    bounds=FIELDS_NUMERIC_OFF if kind=='OFF' else FIELDS_NUMERIC_USDA
    kept=[];actions=[];seen=set();reasons=collections.Counter()
    for line_no,original in enumerate(rows,start=2):
        row=dict(original)
        # Do not change ingredients, nutritional values or valid Nutri-Score labels.
        barcode=(row.get(codecol) or '').strip()
        name=(row.get(namecol) or '').strip()
        row[codecol]=barcode
        row[namecol]=name
        fatal=[]
        if not barcode: fatal.append('missing_barcode')
        if not name: fatal.append('missing_name')
        fatal += check_numeric(row,bounds)
        if barcode and barcode in seen:
            fatal.append('duplicate_identifier')
        if barcode: seen.add(barcode)
        if fatal:
            for reason in fatal:
                reasons[reason]+=1
                actions.append({'dataset':kind,'raw_csv_line':line_no,'barcode':barcode,
                                'action':'EXCLUDE_RECORD','reason':reason,
                                'original_value':row.get(reason.removeprefix('out_of_range_'),''),
                                'new_value':''})
            continue
        if kind=='OFF':
            grade=(row.get('nutriscore_grade') or '').strip().upper()
            if grade and grade not in VALID_GRADE:
                reasons['invalid_nutriscore_to_missing']+=1
                actions.append({'dataset':kind,'raw_csv_line':line_no,'barcode':barcode,
                                'action':'SET_MISSING','reason':'invalid_nutriscore_to_missing',
                                'original_value':grade,'new_value':''})
                grade=''
            row['nutriscore_grade']=grade
            nova=(row.get('nova_group') or '').strip()
            if nova and nova not in {'1','2','3','4'}:
                reasons['invalid_nova_to_missing']+=1
                actions.append({'dataset':kind,'raw_csv_line':line_no,'barcode':barcode,
                                'action':'SET_MISSING','reason':'invalid_nova_to_missing',
                                'original_value':nova,'new_value':''})
                row['nova_group']=''
        kept.append(row)
    return cols,rows,kept,actions,dict(sorted(reasons.items()))


def main():
    if not OFF.is_file() or not USDA.is_file():
        raise SystemExit('Missing original CSVs; do not regenerate using teaching generator accidentally')
    oc,orows,off,oa,or_ = prepare(OFF,'OFF')
    uc,urows,usda,ua,ur_ = prepare(USDA,'USDA')
    PREP.mkdir(parents=True,exist_ok=True)
    AUD.mkdir(parents=True,exist_ok=True)
    write(PREP/'off_products.csv',oc,off)
    write(PREP/'usda_products.csv',uc,usda)
    write(AUD/'cleaning_actions.csv', ['dataset','raw_csv_line','barcode','action','reason','original_value','new_value'], oa+ua)
    codes={r['code']:r for r in off}
    matches=[]
    for r in usda:
        off_row=codes.get(r['gtin_upc'])
        if off_row is None: continue
        eoff=off_row.get('energy_kcal_100g','').strip()
        eusda=r.get('energy_kcal_100g','').strip()
        discrepancy=''
        delta=''
        if eoff and eusda:
            a,b=float(eoff),float(eusda)
            delta=round(b-a,3)
            discrepancy='yes' if abs(delta) > max(10.0,0.1*max(abs(a),1.0)) else 'no'
        matches.append({'barcode':r['gtin_upc'], 'off_name':off_row['product_name'],
                        'usda_name':r['description'], 'off_brand':off_row['brands'],
                        'usda_brand':r['brand_owner'], 'off_energy':eoff,
                        'usda_energy':eusda,'usda_minus_off_kcal_100g':delta,
                        'review_energy_delta':discrepancy})
    matches.sort(key=lambda x:x['barcode'])
    write(AUD/'same_barcode_pairs.csv', ['barcode','off_name','usda_name','off_brand','usda_brand','off_energy','usda_energy','usda_minus_off_kcal_100g','review_energy_delta'],matches)
    summary={
      'dataset_type':'synthetic teaching fixtures, not actual source downloads',
      'original_files':{
        'OFF':{'sha256':hashlib.sha256(OFF.read_bytes()).hexdigest(),'rows':len(orows)},
        'USDA':{'sha256':hashlib.sha256(USDA.read_bytes()).hexdigest(),'rows':len(urows)},
      },
      'cleaning_policy':'Exclude invalid identity or out-of-range/invalid nutrient rows; deduplicate; set invalid score/NOVA to missing; preserve valid reported numeric values',
      'OFF':{'raw_rows':len(orows),'prepared_rows':len(off),'excluded_rows':len(orows)-len(off),
             'with_nutriscore_A_to_E':sum(r['nutriscore_grade'] in VALID_GRADE for r in off),
             'missing_nutriscore':sum(not r['nutriscore_grade'] for r in off),
             'changes':or_},
      'USDA':{'raw_rows':len(urows),'prepared_rows':len(usda),'excluded_rows':len(urows)-len(usda),'changes':ur_},
      'matching':{'exact_shared_barcodes':len(matches),
                  'energy_review_candidates_threshold_10kcal_or_10pct':sum(x['review_energy_delta']=='yes' for x in matches)},
      'notes':[
         'Same barcode is a candidate match, not independent proof of actual product identity.',
         'Nutritional values and labels are synthetic; none were fabricated or corrected to improve GNN F1.',
         'Missing optional nutrient values are preserved for model training-only imputation.',
         'Raw planted errors are preserved unchanged in data/raw for SHACL teaching demonstrations.',
         'Only the existing brand-neighbor GNN is used; sameProductAs links are RDF, not GNN message-passing edges.',
      ]
    }
    (AUD/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('OFF:',len(orows),'raw ->',len(off),'prepared; labelled:',summary['OFF']['with_nutriscore_A_to_E'])
    print('USDA:',len(urows),'raw ->',len(usda),'prepared')
    print('Exact same-barcode candidate pairs:',len(matches))
    print('Wrote data/quality/summary.json, cleaning_actions.csv and same_barcode_pairs.csv')

if __name__=='__main__': main()
