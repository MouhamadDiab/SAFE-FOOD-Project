"""Load the included real OFF sample into deterministic SQL for the pipeline.

Creates normalized allergen/trace tables so R2RML can emit one triple per tag.
Also sets label_gap = 1 when ingredients imply an undeclared allergen (R17).
"""

from __future__ import annotations

import csv
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "sample"
OUT_SQL = HERE / "example.sql"
OUT_DB = HERE / "foodsafe.sqlite"

IMPLIES = {
    "en:milk": re.compile(r"\b(milk|cream|butter|whey|casein|lait|skimmed)\b", re.I),
    "en:gluten": re.compile(r"\b(wheat|barley|rye|gluten|farine de bl[eé])\b", re.I),
    "en:eggs": re.compile(r"\b(egg|eggs|albumin|œuf|oeuf)\b", re.I),
    "en:nuts": re.compile(r"\b(almond|hazelnut|walnut|noisette)\b", re.I),
    "en:soybeans": re.compile(r"\b(soy|soya|tofu)\b", re.I),
    "en:peanuts": re.compile(r"\b(peanut|arachide)\b", re.I),
}

TAG_TO_IRI = {
    "en:milk": "AllergenMilk",
    "en:eggs": "AllergenEggs",
    "en:gluten": "AllergenGluten",
    "en:nuts": "AllergenNuts",
    "en:peanuts": "AllergenPeanuts",
    "en:soybeans": "AllergenSoy",
    "en:sesame-seeds": "AllergenSesame",
    "en:celery": "AllergenCelery",
    "en:mustard": "AllergenMustard",
    "en:fish": "AllergenFish",
    "en:crustaceans": "AllergenCrustaceans",
    "en:sulphur-dioxide-and-sulphites": "AllergenSulphites",
}

GRADE = {"A": "GradeA", "B": "GradeB", "C": "GradeC", "D": "GradeD", "E": "GradeE"}


def esc(v) -> str:
    if v is None or v == "":
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def num(v):
    if v is None or v == "":
        return "NULL"
    try:
        float(v)
        return str(v)
    except (TypeError, ValueError):
        return "NULL"


def split_tags(s: str) -> list[str]:
    if not s or not str(s).strip():
        return []
    return [t.strip() for t in str(s).split(",") if t.strip()]


def label_gap(ingredients: str, allergen_tags: list[str]) -> int:
    have = set(allergen_tags)
    for allergen, rx in IMPLIES.items():
        if rx.search(ingredients or "") and allergen not in have:
            return 1
    return 0


def foodon_class(cat: str) -> str:
    c = (cat or "").lower()
    if "yogurt" in c:
        return "FOODON_03301227"
    if "bread" in c:
        return "FOODON_00001241"
    if "cheese" in c:
        return "FOODON_00001256"
    if "pasta" in c:
        return "FOODON_03301847"
    if "chocolate" in c:
        return "FOODON_03301629"
    if "soda" in c or "soft" in c:
        return "FOODON_03304869"
    return "FOODON_00001002"


def main() -> None:
    off = list(csv.DictReader((SAMPLE / "off_products.csv").open(encoding="utf-8-sig")))
    usda = list(csv.DictReader((SAMPLE / "usda_products.csv").open(encoding="utf-8-sig")))

    # Deduplicate by barcode; duplicates, if any, must be reported explicitly.
    seen = set()
    off_unique = []
    for r in off:
        if r["code"] in seen:
            continue
        seen.add(r["code"])
        off_unique.append(r)

    if len(off_unique) != len(off):
        print(f"WARNING: dropped {len(off)-len(off_unique)} duplicate OFF barcode rows")

    lines = [
        "DROP TABLE IF EXISTS off_products;",
        "DROP TABLE IF EXISTS off_allergens;",
        "DROP TABLE IF EXISTS off_traces;",
        "DROP TABLE IF EXISTS usda_products;",
        """CREATE TABLE off_products (
  code TEXT PRIMARY KEY, product_name TEXT, brands TEXT, categories_tags TEXT,
  ingredients_text TEXT, nutriscore_grade TEXT, nutri_iri TEXT, nova_group TEXT,
  countries_tags TEXT, energy_kcal_100g REAL, fat_100g REAL, saturated_fat_100g REAL,
  carbohydrates_100g REAL, sugars_100g REAL, proteins_100g REAL, salt_100g REAL,
  fiber_100g REAL, label_gap INTEGER, foodon_class TEXT, source TEXT, retrieved_date TEXT
);""",
        """CREATE TABLE off_allergens (
  code TEXT, allergen_tag TEXT, allergen_iri TEXT
);""",
        """CREATE TABLE off_traces (
  code TEXT, allergen_tag TEXT, allergen_iri TEXT
);""",
        """CREATE TABLE usda_products (
  gtin_upc TEXT PRIMARY KEY, description TEXT, brand_owner TEXT,
  energy_kcal_100g REAL, fat_100g REAL, sugars_100g REAL,
  proteins_100g REAL, salt_100g REAL, source TEXT, retrieved_date TEXT
);""",
    ]

    allergen_rows = []
    trace_rows = []

    for r in off_unique:
        atags = split_tags(r["allergens_tags"])
        gap = label_gap(r["ingredients_text"], atags)
        grade = (r["nutriscore_grade"] or "").strip().upper()
        nutri_iri = GRADE.get(grade, "")
        lines.append(
            "INSERT INTO off_products VALUES ("
            + ",".join([
                esc(r["code"]), esc(r["product_name"]), esc(r["brands"]),
                esc(r["categories_tags"]), esc(r["ingredients_text"]),
                esc(grade), esc(nutri_iri), esc(r["nova_group"]),
                esc(r["countries_tags"]),
                num(r["energy_kcal_100g"]), num(r["fat_100g"]),
                num(r["saturated_fat_100g"]), num(r["carbohydrates_100g"]),
                num(r["sugars_100g"]), num(r["proteins_100g"]),
                num(r["salt_100g"]), num(r["fiber_100g"]),
                str(gap), esc(foodon_class(r["categories_tags"])),
                esc(r["source"]), esc(r["retrieved_date"]),
            ])
            + ");"
        )
        for t in atags:
            iri = TAG_TO_IRI.get(t)
            if iri:
                allergen_rows.append((r["code"], t, iri))
        for t in split_tags(r["traces_tags"]):
            iri = TAG_TO_IRI.get(t)
            if iri:
                trace_rows.append((r["code"], t, iri))

    for code, tag, iri in allergen_rows:
        lines.append(f"INSERT INTO off_allergens VALUES ({esc(code)},{esc(tag)},{esc(iri)});")
    for code, tag, iri in trace_rows:
        lines.append(f"INSERT INTO off_traces VALUES ({esc(code)},{esc(tag)},{esc(iri)});")

    for r in usda:
        lines.append(
            "INSERT OR IGNORE INTO usda_products VALUES ("
            + ",".join([
                esc(r["gtin_upc"]), esc(r["description"]), esc(r["brand_owner"]),
                num(r["energy_kcal_100g"]), num(r["fat_100g"]),
                num(r["sugars_100g"]), num(r["proteins_100g"]),
                num(r["salt_100g"]), esc(r["source"]), esc(r["retrieved_date"]),
            ])
            + ");"
        )

    OUT_SQL.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if OUT_DB.exists():
        OUT_DB.unlink()
    con = sqlite3.connect(OUT_DB)
    con.executescript(OUT_SQL.read_text(encoding="utf-8"))
    con.close()
    print(
        f"Wrote {OUT_SQL.name}: {len(off_unique)} OFF products, "
        f"{len(allergen_rows)} allergen rows, {len(usda)} USDA"
    )


if __name__ == "__main__":
    main()
