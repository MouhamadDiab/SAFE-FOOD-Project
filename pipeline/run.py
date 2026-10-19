"""SAFE-FOOD pipeline: SQL source -> RDF -> SHACL gate -> VoID -> Fuseki.

  python pipeline/run.py
  python pipeline/run.py --no-load
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

import requests
from pyshacl import validate
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
SH = Namespace("http://www.w3.org/ns/shacl#")
FUSEKI = os.environ.get("FUSEKI_URL", "http://127.0.0.1:3030")
DATASET = os.environ.get("FUSEKI_DATASET", "kr")


def step(n, text):
    print(f"{n} {text}", flush=True)


def source() -> Path:
    BUILD.mkdir(exist_ok=True)
    db = BUILD / "example.sqlite"
    db.unlink(missing_ok=True)
    sql = ROOT / "data" / "example.sql"
    if not sql.exists():
        sys.exit("Missing data/example.sql — run: python data/fetch_or_build_sample.py && python data/build_example_sql.py")
    con = sqlite3.connect(db)
    con.executescript(sql.read_text(encoding="utf-8"))
    con.close()
    step(1, f"source: data/example.sql -> {db}")
    return db


def materialize(db: Path) -> Path:
    sys.path.insert(0, str(ROOT / "mapping"))
    from materialize import materialize as mat
    out = BUILD / "graph.nt"
    n = mat(db, out)
    step(2, f"map: {n:,} triples -> build/graph.nt")
    return out


def gate(graph_path: Path) -> None:
    data = Graph()
    data.parse(graph_path, format="nt")
    data.parse(ROOT / "ontology" / "foodon-slim.ttl", format="turtle")
    data.parse(ROOT / "ontology" / "foodsafe.ttl", format="turtle")
    shapes = Graph().parse(ROOT / "shapes" / "shapes.ttl", format="turtle")
    conforms, report, text = validate(
        data, shacl_graph=shapes, inference="rdfs", allow_warnings=True
    )
    (BUILD / "shacl-report.txt").write_text(text, encoding="utf-8")
    violations = len(list(report.subjects(SH.resultSeverity, SH.Violation)))
    warnings = len(list(report.subjects(SH.resultSeverity, SH.Warning)))
    step(3, f"validate: {violations} Violation, {warnings} Warning -> build/shacl-report.txt")
    if violations or not conforms:
        sys.exit("SHACL gate: Violations present; endpoint not loaded. See build/shacl-report.txt")


def describe(graph_path: Path) -> None:
    sys.path.insert(0, str(ROOT / "access-layer"))
    from make_void import write_void
    n = write_void(graph_path, BUILD / "void.ttl")
    step(4, f"describe: {n} VoID triples -> build/void.ttl")


def load(graph_path: Path) -> None:
    base = f"{FUSEKI}/{DATASET}"
    for _ in range(30):
        try:
            if requests.get(f"{FUSEKI}/$/ping", timeout=5).ok:
                break
        except requests.ConnectionError:
            pass
        time.sleep(2)
    else:
        sys.exit(f"Endpoint at {FUSEKI} did not answer within a minute.")
    ont = (
        (ROOT / "ontology" / "foodon-slim.ttl").read_bytes()
        + b"\n"
        + (ROOT / "ontology" / "foodsafe.ttl").read_bytes()
    )
    r1 = requests.put(
        f"{base}/data?default",
        data=graph_path.read_bytes(),
        headers={"Content-Type": "application/n-triples"},
        timeout=300,
    )
    r2 = requests.post(
        f"{base}/data?default",
        data=ont,
        headers={"Content-Type": "text/turtle"},
        timeout=60,
    )
    for r in (r1, r2):
        if not r.ok:
            sys.exit(f"Loading failed ({r.status_code}): {r.text[:200]}")
    step(5, f"load: graph and ontology -> {base}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-load", action="store_true")
    a = ap.parse_args()
    BUILD.mkdir(exist_ok=True)
    graph = materialize(source())
    gate(graph)
    describe(graph)
    if not a.no_load:
        load(graph)
    print("done")


if __name__ == "__main__":
    main()
