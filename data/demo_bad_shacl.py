"""Safe SHACL failure demonstration on ONE synthetic raw bad record.

Creates an in-memory RDF test graph; does NOT modify prepared CSVs, SQLite,
Fuseki, or the validated production graph. A violation is the expected PASS.
"""
from __future__ import annotations
import csv
from decimal import Decimal
from pathlib import Path
from rdflib import Graph, Literal, Namespace, URIRef, RDF, XSD
from pyshacl import validate
ROOT=Path(__file__).resolve().parents[1]
FS=Namespace('https://ul.edu.lb/kr/foodsafe#')
SH=Namespace('http://www.w3.org/ns/shacl#')

def main():
    with (ROOT/'data/raw/off_products_original.csv').open(encoding='utf-8-sig',newline='') as f:
        bad=next(r for r in csv.DictReader(f)
                 if r['energy_kcal_100g'] and float(r['energy_kcal_100g']) < 0)
    s=URIRef('https://ul.edu.lb/kr/food/id/product/off/demo-bad-row')
    g=Graph()
    g.add((s,RDF.type,FS.PackagedProduct))
    g.add((s,FS.barcode,Literal(bad['code'],datatype=XSD.string)))
    g.add((s,FS.productName,Literal(bad['product_name'],datatype=XSD.string)))
    g.add((s,FS.energyKcal100g,Literal(Decimal(bad['energy_kcal_100g']),datatype=XSD.decimal)))
    g.parse(ROOT/'ontology/foodsafe.ttl',format='turtle')
    g.parse(ROOT/'ontology/foodon-slim.ttl',format='turtle')
    shapes=Graph().parse(ROOT/'shapes/shapes.ttl',format='turtle')
    conforms,report,text=validate(g,shacl_graph=shapes,inference='rdfs',allow_warnings=True)
    violations=len(list(report.subjects(SH.resultSeverity,SH.Violation)))
    print('Raw bad-row barcode:',bad['code'])
    print('Raw energy:',bad['energy_kcal_100g'],'kcal/100g')
    print('SHACL conforms:',conforms,'| violations:',violations)
    print('Expected: False and at least 1 Violation (in-memory demo only)')
    if conforms or not violations:raise SystemExit('ERROR: intentionally bad record was not flagged')
    print('PASS: SHACL caught planted negative energy; clean graph and CSVs untouched')

if __name__=='__main__':main()
