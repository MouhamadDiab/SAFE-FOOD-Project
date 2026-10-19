"""Verify SAFE-FOOD's declarative R2RML with Morph-KGC against Python output.

Runs INDEPENDENTLY of the default pipeline, does not change committed files.
Execute from repository root in a separate Python/Docker environment where
morph_kgc is installed, e.g. see FINAL_CHECK.ps1.
"""
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import XSD

ROOT = Path(__file__).resolve().parents[1]
SQLITE = ROOT / 'build' / 'example.sqlite'
NT = ROOT / 'build' / 'graph.nt'
MAPPING = ROOT / 'mapping' / 'mapping.ttl'


def canonical_value(node):
    if not isinstance(node, Literal):
        return ('IRI', str(node))
    datatype = str(node.datatype or XSD.string)
    if datatype in {str(XSD.decimal), str(XSD.integer), str(XSD.double), str(XSD.float)}:
        try:
            return ('literal-number', str(Decimal(str(node)).normalize()))
        except InvalidOperation:
            pass
    if datatype == str(XSD.boolean):
        return ('literal-boolean', str(node).strip().lower() in {'true', '1'})
    return ('literal', datatype, node.language, str(node))


def canonical_graph(graph):
    return {(str(s), str(p), canonical_value(o)) for s, p, o in graph}


def main():
    if not SQLITE.exists() or not NT.exists():
        raise SystemExit('Missing build/example.sqlite or build/graph.nt; run docker compose up -d first.')
    try:
        import morph_kgc
    except ImportError:
        raise SystemExit('Morph-KGC missing. Use the isolated Docker command in FINAL_CHECK.ps1.')

    mapping = MAPPING.resolve().as_posix()
    db = SQLITE.resolve().as_posix()
    # sqlite absolute path: sqlite:////work/build/example.sqlite in Linux.
    config = f'''[CONFIGURATION]\nlogging_level: ERROR\n\n[DataSource1]\nmappings: {mapping}\ndb_url: sqlite:///{db}\n'''
    print('Verifying R2RML with the actual Morph-KGC engine...', flush=True)
    print('Database:', SQLITE.relative_to(ROOT), flush=True)
    print('Mapping:', MAPPING.relative_to(ROOT), flush=True)
    r2rml_graph = morph_kgc.materialize(config)
    python_graph = Graph().parse(NT, format='nt')
    engine_set = canonical_graph(r2rml_graph)
    python_set = canonical_graph(python_graph)
    missing = sorted(python_set - engine_set)
    extra = sorted(engine_set - python_set)
    print('R2RML triples:', len(r2rml_graph))
    print('Python triples:', len(python_graph))
    print('Missing in R2RML (semantic comparison):', len(missing))
    print('Only in R2RML (semantic comparison):', len(extra))
    if missing or extra:
        print('MAPPING PARITY NOT CONFIRMED')
        if missing:
            print('Sample missing triples:')
            for t in missing[:5]:
                print('  ', t)
        if extra:
            print('Sample extra triples:')
            for t in extra[:5]:
                print('  ', t)
        raise SystemExit(2)
    print('PASS: R2RML and Python mapping agree on this current prepared Option A snapshot.')


if __name__ == '__main__':
    main()
