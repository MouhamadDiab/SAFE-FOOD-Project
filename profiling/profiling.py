"""One-pass profile of the exact included 50-product OFF sample."""
from pathlib import Path
from collections import Counter
import csv,json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/sample/off_products.csv'
OUT=ROOT/'profiling/reports/summary.json'

def main():
    with SOURCE.open(encoding='utf-8-sig', newline='') as f:
        rows=list(csv.DictReader(f))
    codes=[r['code'] for r in rows]
    tags=[tag for r in rows for tag in r['allergens_tags'].split(',') if tag]
    nutrition=['energy_kcal_100g','fat_100g','sugars_100g','proteins_100g','salt_100g']
    report={'source':'Open Food Facts API snapshot (2026-10-19)',
       'products':len(rows),'unique_barcodes':len(set(codes)),
       'brands':len(set(r['brands'].strip().lower() for r in rows)),
       'with_declared_allergen_tags':sum(bool(r['allergens_tags'].strip()) for r in rows),
       'missing_nutrients':{c:sum(not r[c].strip() for r in rows) for c in nutrition},
       'reported_nutriscore':dict(Counter(r['nutriscore_grade'].strip() or 'missing' for r in rows)),
       'raw_declared_tag_counts':dict(Counter(tags))}
    OUT.parent.mkdir(exist_ok=True,parents=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
