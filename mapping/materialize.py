"""Materialize the SQL source to RDF with NO quality-based row filtering.

The SHACL gate, rather than this mapper, must detect bad required fields and
out-of-range nutrient values. This is the Python implementation used by CI;
see mapping/mapping.ttl for the declarative R2RML representation.
"""

from __future__ import annotations

import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef, XSD, RDF, OWL

ROOT = Path(__file__).resolve().parents[1]
FS = Namespace("https://ul.edu.lb/kr/foodsafe#")
FOODON = Namespace("http://purl.obolibrary.org/obo/")
ID = "https://ul.edu.lb/kr/food/id/product/"


def ok_energy(v) -> bool:
    if v is None:
        return True
    try:
        x = float(v)
        return 0 <= x <= 900
    except (TypeError, ValueError):
        return False


def ok_fat(v) -> bool:
    if v is None:
        return True
    try:
        x = float(v)
        return 0 <= x <= 100
    except (TypeError, ValueError):
        return False


def lit_dec(v):
    if v is None:
        return None
    try:
        d = Decimal(str(v))
        if not d.is_finite():
            raise ValueError("nonfinite")
        return Literal(d, datatype=XSD.decimal)
    except (TypeError, ValueError, InvalidOperation):
        return Literal(str(v), datatype=XSD.string)  # SHACL flags invalid numeric datatype


def materialize(db_path: Path, out_path: Path) -> int:
    g = Graph()
    g.bind("foodsafe", FS)
    g.bind("foodon", FOODON)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    for r in con.execute("SELECT rowid, * FROM off_products"):
        name = (r["product_name"] or "").strip()
        code = (r["code"] or "").strip()
        # Even malformed rows must become SHACL targets; missing barcode gets a
        # deterministic row placeholder but retains its original empty literal.
        subject_id = code if code else f"invalid-row-{r['rowid']}"
        s = URIRef(f"{ID}off/{subject_id}")
        g.add((s, RDF.type, FS.PackagedProduct))
        # FoodOn typing
        fc = r["foodon_class"] or "FOODON_00001002"
        g.add((s, RDF.type, FOODON[fc]))
        g.add((s, FS.barcode, Literal(code, datatype=XSD.string)))
        g.add((s, FS.productName, Literal(name, datatype=XSD.string)))
        if r["brands"]:
            g.add((s, FS.brandName, Literal(r["brands"], datatype=XSD.string)))
        if r["ingredients_text"]:
            g.add((s, FS.ingredientsText, Literal(r["ingredients_text"], datatype=XSD.string)))
        if r["categories_tags"]:
            g.add((s, FS.hasCategoryTag, Literal(r["categories_tags"], datatype=XSD.string)))
        for col, pred in [
            ("energy_kcal_100g", FS.energyKcal100g),
            ("fat_100g", FS.fat100g),
            ("sugars_100g", FS.sugars100g),
            ("proteins_100g", FS.proteins100g),
            ("salt_100g", FS.salt100g),
        ]:
            lit = lit_dec(r[col])
            if lit is not None:
                g.add((s, pred, lit))
        if r["nutri_iri"]:
            g.add((s, FS.hasNutriScore, FS[r["nutri_iri"]]))
        if r["label_gap"]:
            g.add((s, FS.hasLabelGapFlag, Literal(True, datatype=XSD.boolean)))
        g.add((s, FS.fromSource, FS.SourceOFF))
        if r["retrieved_date"]:
            g.add((s, FS.retrievedOn, Literal(r["retrieved_date"], datatype=XSD.date)))

    for r in con.execute("SELECT * FROM off_allergens"):
        s = URIRef(f"{ID}off/{r['code']}")
        if (s, RDF.type, FS.PackagedProduct) in g:
            g.add((s, FS.hasDeclaredAllergen, FS[r["allergen_iri"]]))

    for r in con.execute("SELECT * FROM off_traces"):
        s = URIRef(f"{ID}off/{r['code']}")
        if (s, RDF.type, FS.PackagedProduct) in g:
            g.add((s, FS.mayContainAllergen, FS[r["allergen_iri"]]))

    for r in con.execute("SELECT rowid, * FROM usda_products"):
        code = (r["gtin_upc"] or "").strip()
        name = (r["description"] or "").strip()
        subject_id = code if code else f"invalid-row-{r['rowid']}"
        s = URIRef(f"{ID}usda/{subject_id}")
        g.add((s, RDF.type, FS.PackagedProduct))
        g.add((s, FS.barcode, Literal(code, datatype=XSD.string)))
        g.add((s, FS.productName, Literal(name, datatype=XSD.string)))
        if r["brand_owner"]:
            g.add((s, FS.brandName, Literal(r["brand_owner"], datatype=XSD.string)))
        for col, pred in [
            ("energy_kcal_100g", FS.energyKcal100g),
            ("fat_100g", FS.fat100g),
            ("sugars_100g", FS.sugars100g),
            ("proteins_100g", FS.proteins100g),
            ("salt_100g", FS.salt100g),
        ]:
            lit = lit_dec(r[col])
            if lit is not None:
                g.add((s, pred, lit))
        g.add((s, FS.fromSource, FS.SourceUSDA))
        if r["retrieved_date"]:
            g.add((s, FS.retrievedOn, Literal(r["retrieved_date"], datatype=XSD.date)))
        # sameProductAs when OFF twin exists
        off = URIRef(f"{ID}off/{code}")
        if (off, RDF.type, FS.PackagedProduct) in g:
            g.add((s, FS.sameProductAs, off))
            g.add((off, FS.sameProductAs, s))

    con.close()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(out_path, format="nt")
    print(f"materialize: {len(g):,} triples -> {out_path} (no quality-based row filtering)")
    return len(g)


if __name__ == "__main__":
    db = ROOT / "build" / "example.sqlite"
    if not db.exists():
        db = ROOT / "data" / "foodsafe.sqlite"
    materialize(db, ROOT / "build" / "graph.nt")
