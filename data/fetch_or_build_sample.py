"""Build the SAFE-FOOD teaching sample (OFF-shaped + USDA-shaped CSVs).

Creates ~3,000 Open Food Facts–style product rows and ~800 USDA branded-food
rows with deliberate barcode overlap for entity resolution, plus planted
quality issues for the constraint inventory (Session 1 pattern).

Optionally enriches a subset from the live Open Food Facts API when
SAFEFOOD_FETCH_LIVE=1 and the network is available.
"""

from __future__ import annotations

import csv
import hashlib
import os
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "sample"
RNG = random.Random(42)

BRANDS = [
    "Nestle", "Nestlé", "Danone", "Kraft", "Unilever", "PepsiCo",
    "Coca-Cola", "Kellogg", "General Mills", "Barilla", "Heinz",
    "Almarai", "LibanPack", "Bonjus", "Candia", "President",
]
CATEGORIES = [
    "en:yogurts", "en:chocolates", "en:breads", "en:breakfast-cereals",
    "en:sodas", "en:cheeses", "en:cookies", "en:plant-based-milks",
    "en:pastas", "en:ready-meals", "en:fruit-juices", "en:waters",
]
ALLERGENS = [
    "en:milk", "en:eggs", "en:gluten", "en:nuts", "en:peanuts",
    "en:soybeans", "en:sesame-seeds", "en:celery", "en:mustard",
    "en:fish", "en:crustaceans", "en:sulphur-dioxide-and-sulphites",
]
NUTRI = list("ABCDE")
COUNTRIES = ["en:lebanon", "en:france", "en:united-states", "en:germany", "en:italy"]

# Ingredients snippets that imply allergens (for label-gap rules)
IMPLIES = {
    "en:milk": ["milk", "skimmed milk", "cream", "butter", "whey", "casein", "lait"],
    "en:gluten": ["wheat flour", "barley", "rye", "gluten", "farine de blé"],
    "en:eggs": ["egg", "eggs", "albumin", "œuf"],
    "en:nuts": ["almond", "hazelnut", "walnut", "noisette"],
    "en:soybeans": ["soy", "soya", "tofu", "lecithin (soy)"],
    "en:peanuts": ["peanut", "arachide"],
    "en:sesame-seeds": ["sesame", "sesame seeds", "tahini"],
    "en:celery": ["celery", "céléri"],
    "en:mustard": ["mustard", "moutarde"],
    "en:fish": ["fish", "cod", "salmon", "poisson"],
    "en:crustaceans": ["shrimp", "crab", "crustacean"],
    "en:sulphur-dioxide-and-sulphites": ["sulphite", "sulfite", "E220"],
}


def barcode(n: int) -> str:
    """Deterministic EAN-13-like code (not a real checksum; teaching only)."""
    raw = f"3{n:012d}"
    return raw[:13]


def product_name(i: int, brand: str, cat: str) -> str:
    kind = cat.split(":")[-1].replace("-", " ")
    return f"{brand} {kind.title()} {i % 97}"


def ingredients_for(allergens: list[str], force_gap: bool) -> tuple[str, str]:
    """Return (ingredients_text, allergens_tags)."""
    parts = ["water", "sugar", "salt"]
    tags = list(allergens)
    if force_gap and allergens:
        # Mention allergen in text but omit from tags (label gap)
        a = allergens[0]
        parts.append(RNG.choice(IMPLIES[a]))
        tags = [t for t in tags if t != a]
    else:
        for a in allergens:
            parts.append(RNG.choice(IMPLIES[a]))
    if RNG.random() < 0.15:
        parts.append("natural flavouring")
    return ", ".join(parts), ",".join(tags)


def nutri_values(ok: bool) -> dict:
    if not ok:
        # Planted sanity failures
        return {
            "energy_kcal_100g": RNG.choice([-10, 1200, 50]),
            "fat_100g": RNG.choice([-1, 150, 3.0]),
            "saturated_fat_100g": 1.0,
            "carbohydrates_100g": 20.0,
            "sugars_100g": 10.0,
            "proteins_100g": 5.0,
            "salt_100g": 0.5,
            "fiber_100g": 1.0,
        }
    fat = round(RNG.uniform(0, 40), 2)
    sugars = round(RNG.uniform(0, 30), 2)
    proteins = round(RNG.uniform(0, 25), 2)
    carbs = round(min(100, sugars + RNG.uniform(0, 40)), 2)
    salt = round(RNG.uniform(0, 3), 3)
    energy = round(fat * 9 + carbs * 4 + proteins * 4, 1)
    return {
        "energy_kcal_100g": energy,
        "fat_100g": fat,
        "saturated_fat_100g": round(fat * RNG.uniform(0.2, 0.6), 2),
        "carbohydrates_100g": carbs,
        "sugars_100g": sugars,
        "proteins_100g": proteins,
        "salt_100g": salt,
        "fiber_100g": round(RNG.uniform(0, 8), 2),
    }


OFF_FIELDS = [
    "code", "product_name", "brands", "categories_tags", "allergens_tags",
    "traces_tags", "ingredients_text", "nutriscore_grade", "nova_group",
    "countries_tags", "energy_kcal_100g", "fat_100g", "saturated_fat_100g",
    "carbohydrates_100g", "sugars_100g", "proteins_100g", "salt_100g",
    "fiber_100g", "source", "retrieved_date",
]


def build_off(n: int = 3000) -> list[dict]:
    rows = []
    for i in range(n):
        brand = RNG.choice(BRANDS)
        cat = RNG.choice(CATEGORIES)
        code = barcode(100000 + i)
        n_all = RNG.randint(0, 3)
        allergens = RNG.sample(ALLERGENS, n_all) if n_all else []
        force_gap = (i % 17 == 0) and bool(allergens)
        force_opaque = (i % 41 == 0)
        force_bad_nutri = (i % 53 == 0)
        force_bad_score = (i % 59 == 0)
        force_missing_name = (i % 101 == 0)
        force_dup_later = (i == 50)  # duplicate barcode planted at i==3050 via append

        if force_opaque:
            ingredients, tags = "", ""
            allergens = []
        else:
            ingredients, tags = ingredients_for(allergens or (["en:milk"] if force_gap else []), force_gap)

        nut = nutri_values(ok=not force_bad_nutri)
        grade = ""
        if not force_opaque and RNG.random() < 0.7:
            grade = "Z" if force_bad_score else RNG.choice(NUTRI)
        elif not force_opaque and all(nut[k] is not None for k in ("fat_100g", "sugars_100g", "proteins_100g")):
            # complete macros but missing score — Warning family
            if i % 23 == 0:
                grade = ""

        nova = ""
        if RNG.random() < 0.4:
            nova = str(RNG.choice([1, 2, 3, 4, 9] if force_bad_score else [1, 2, 3, 4]))

        traces = ""
        if allergens and RNG.random() < 0.2:
            # sometimes traces duplicates a declared allergen
            traces = allergens[0] if i % 29 == 0 else RNG.choice(ALLERGENS)

        row = {
            "code": code,
            "product_name": "" if force_missing_name else product_name(i, brand, cat),
            "brands": brand,
            "categories_tags": "" if force_opaque and i % 2 == 0 else cat,
            "allergens_tags": tags,
            "traces_tags": traces,
            "ingredients_text": ingredients,
            "nutriscore_grade": grade,
            "nova_group": nova,
            "countries_tags": RNG.choice(COUNTRIES),
            **nut,
            "source": "openfoodfacts",
            "retrieved_date": "2026-10-18",
        }
        # Partial nutrition: energy without macros
        if i % 37 == 0 and not force_bad_nutri:
            row["fat_100g"] = ""
            row["proteins_100g"] = ""
            row["carbohydrates_100g"] = ""
        rows.append(row)

    # Duplicate barcode with conflicting allergens (identity rule)
    clash = dict(rows[50])
    clash["product_name"] = clash["product_name"] + " DUPLICATE"
    clash["allergens_tags"] = "en:peanuts"
    clash["code"] = rows[50]["code"]
    rows.append(clash)
    return rows


def build_usda(off_rows: list[dict], n: int = 800) -> list[dict]:
    """USDA-shaped rows; first ~150 share barcodes with OFF for ER."""
    rows = []
    overlap = off_rows[:150]
    for i in range(n):
        if i < len(overlap):
            src = overlap[i]
            code = src["code"]
            # slight name/brand noise for fuzzy ER
            name = (src["product_name"] or "Unknown") + (" Ltd" if i % 5 == 0 else "")
            brand = src["brands"].replace("é", "e") if i % 3 == 0 else src["brands"]
            # occasional nutrient clash
            energy = src["energy_kcal_100g"]
            if i % 11 == 0 and energy not in ("", None):
                try:
                    energy = round(float(energy) * 1.45, 1)
                except (TypeError, ValueError):
                    pass
            salt = src["salt_100g"]
        else:
            code = barcode(900000 + i)
            name = f"USDA Branded Item {i}"
            brand = RNG.choice(BRANDS)
            energy = round(RNG.uniform(20, 500), 1)
            salt = round(RNG.uniform(0, 2), 3)

        rows.append({
            "gtin_upc": code,
            "description": name,
            "brand_owner": brand,
            "energy_kcal_100g": energy if i < len(overlap) else energy,
            "fat_100g": round(RNG.uniform(0, 30), 2),
            "sugars_100g": round(RNG.uniform(0, 25), 2),
            "proteins_100g": round(RNG.uniform(0, 20), 2),
            "salt_100g": salt if i < len(overlap) else round(RNG.uniform(0, 2), 3),
            "source": "usda_fdc",
            "retrieved_date": "2026-10-18",
        })
    return rows


def try_live_enrich(rows: list[dict], limit: int = 40) -> list[dict]:
    if os.environ.get("SAFEFOOD_FETCH_LIVE") != "1":
        return rows
    try:
        import urllib.request
        import json
        url = (
            "https://world.openfoodfacts.org/cgi/search.pl?"
            "action=process&json=true&page_size=40&fields="
            "code,product_name,brands,categories_tags,allergens_tags,"
            "traces_tags,ingredients_text,nutriscore_grade,nova_group,"
            "countries_tags,nutriments"
        )
        with urllib.request.urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        live = payload.get("products", [])[:limit]
        for j, p in enumerate(live):
            nut = p.get("nutriments") or {}
            rows[j].update({
                "code": str(p.get("code") or rows[j]["code"]),
                "product_name": p.get("product_name") or rows[j]["product_name"],
                "brands": p.get("brands") or rows[j]["brands"],
                "ingredients_text": p.get("ingredients_text") or rows[j]["ingredients_text"],
                "allergens_tags": ",".join(p.get("allergens_tags") or []) or rows[j]["allergens_tags"],
                "nutriscore_grade": (p.get("nutriscore_grade") or "").upper() or rows[j]["nutriscore_grade"],
                "energy_kcal_100g": nut.get("energy-kcal_100g", rows[j]["energy_kcal_100g"]),
                "fat_100g": nut.get("fat_100g", rows[j]["fat_100g"]),
                "sugars_100g": nut.get("sugars_100g", rows[j]["sugars_100g"]),
                "proteins_100g": nut.get("proteins_100g", rows[j]["proteins_100g"]),
                "salt_100g": nut.get("salt_100g", rows[j]["salt_100g"]),
                "source": "openfoodfacts+api",
            })
        print(f"Enriched {len(live)} rows from Open Food Facts API")
    except Exception as e:
        print(f"Live enrich skipped: {e}")
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    SAMPLE.mkdir(parents=True, exist_ok=True)
    off = build_off(3000)
    off = try_live_enrich(off)
    usda = build_usda(off, 800)
    write_csv(SAMPLE / "off_products.csv", OFF_FIELDS, off)
    usda_fields = [
        "gtin_upc", "description", "brand_owner", "energy_kcal_100g",
        "fat_100g", "sugars_100g", "proteins_100g", "salt_100g",
        "source", "retrieved_date",
    ]
    write_csv(SAMPLE / "usda_products.csv", usda_fields, usda)
    digest = hashlib.sha256((SAMPLE / "off_products.csv").read_bytes()).hexdigest()[:12]
    print(f"Wrote {len(off)} OFF rows, {len(usda)} USDA rows (sha256={digest})")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] != ["--allow-synthetic-overwrite"]:
        raise SystemExit("STOP: Option A uses prepared synthetic inputs. "
                         "This legacy script would overwrite the prepared samples "
                         "with synthetic data. Explicit opt-in: --allow-synthetic-overwrite")
    main()
