"""Summary checks from the actual included real sample (not patient safety)."""
from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'build/example.sqlite'

def main():
    if not DB.exists(): raise SystemExit('Run python pipeline/run.py --no-load first')
    with sqlite3.connect(DB) as db:
        products=db.execute('SELECT COUNT(*) FROM off_products').fetchone()[0]
        gaps=db.execute('SELECT COUNT(*) FROM off_products WHERE label_gap=1').fetchone()[0]
        missing_salt=db.execute('SELECT COUNT(*) FROM off_products WHERE salt_100g IS NULL').fetchone()[0]
        zeros=db.execute('SELECT COUNT(*) FROM off_products WHERE salt_100g=0').fetchone()[0]
        other=db.execute('SELECT COUNT(*) FROM usda_products').fetchone()[0]
    print(f'OFF products={products}; review flags={gaps}; salt missing={missing_salt}; salt zero={zeros}; USDA rows={other}')

if __name__=='__main__':main()
