"""Report genuine exact-barcode OFF-USDA overlap, if independently sourced USDA data exists."""
from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'build/example.sqlite'

def main():
    if not DB.exists(): raise SystemExit('Run the pipeline first')
    with sqlite3.connect(DB) as db:
        count=db.execute('SELECT COUNT(*) FROM off_products o JOIN usda_products u ON o.code=u.gtin_upc').fetchone()[0]
    print(f'Exact-barcode OFF-USDA overlaps in the provided database: {count}')
    if not count:print('No separate USDA data: precision/recall and genuine entity resolution not evaluated.')
if __name__=='__main__':main()
