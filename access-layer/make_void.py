"""Create a compact VoID schema using RDFLib (no external VoID service)."""
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict

from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

ROOT = Path(__file__).resolve().parents[1]
NS = "https://ul.edu.lb/kr/foodsafe#"
DATASET = URIRef("https://ul.edu.lb/kr/foodsafe/void")
VOID = Namespace("http://rdfs.org/ns/void#")
VEXT = Namespace("http://ldf.fi/void-ext#")


def write_void(graph_path, out_path):
    data = Graph().parse(graph_path, format="nt" if str(graph_path).endswith(".nt") else "turtle")
    out = Graph()
    out.bind("void", VOID)
    out.bind("void-ext", VEXT)
    out.bind("foodsafe", Namespace(NS))
    members = defaultdict(set)
    for node, cls in data.subject_objects(RDF.type):
        if str(cls).startswith(NS):
            members[cls].add(node)
    for cls, nodes in members.items():
        cp = URIRef(f"{NS}partition-{str(cls).split('#')[-1]}")
        out.add((DATASET, VOID.classPartition, cp))
        out.add((cp, VOID["class"], cls))
        out.add((cp, VOID.entities, Literal(len(nodes), datatype=XSD.integer)))
        counts = defaultdict(int)
        kinds = defaultdict(set)
        for n in nodes:
            for p, o in data.predicate_objects(n):
                if p == RDF.type or not str(p).startswith(NS):
                    continue
                counts[p] += 1
                if isinstance(o, Literal):
                    kinds[p].add(("datatype", o.datatype or XSD.string))
                else:
                    for obj_cls in data.objects(o, RDF.type):
                        kinds[p].add(("class", obj_cls))
        for pred, count in counts.items():
            pp = URIRef(f"{cp}-{str(pred).split('#')[-1]}")
            out.add((cp, VOID.propertyPartition, pp))
            out.add((pp, VOID.property, pred))
            out.add((pp, VOID.triples, Literal(count, datatype=XSD.integer)))
            for kind, value in kinds[pred]:
                suffix = str(value).split('#')[-1].split('/')[-1]
                part = URIRef(f"{pp}-{kind}-{suffix}")
                if kind == "class":
                    out.add((pp, VOID.classPartition, part))
                    out.add((part, VOID["class"], value))
                else:
                    out.add((pp, VEXT.datatypePartition, part))
                    out.add((part, VEXT.datatype, value))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out.serialize(out_path, format="turtle")
    return len(out)

if __name__ == "__main__":
    print(write_void(sys.argv[1], sys.argv[2]), "VoID triples")
