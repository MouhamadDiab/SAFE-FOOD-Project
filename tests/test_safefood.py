from pathlib import Path
import csv,sqlite3,sys,tempfile
import pytest
from rdflib import Graph,Namespace,RDF,Literal
from rdflib.namespace import XSD

ROOT=Path(__file__).resolve().parents[1]
FS=Namespace('https://ul.edu.lb/kr/foodsafe#')


def test_real_snapshot_integrity():
    with (ROOT/'data/sample/off_products.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==50
    assert len({r['code'] for r in rows})==50
    assert sum(bool(r['energy_kcal_100g']) for r in rows)==50
    assert sum(bool(r['salt_100g']) for r in rows)==48
    assert sum(r['salt_100g'].strip()=='0' for r in rows)==24


def test_ontology_shapes_r2rml_parse():
    for f in ['ontology/foodon-slim.ttl','ontology/foodsafe.ttl','shapes/shapes.ttl','mapping/mapping.ttl']:
        assert len(Graph().parse(ROOT/f,format='turtle'))>10
    rr=Namespace('http://www.w3.org/ns/r2rml#')
    maps=Graph().parse(ROOT/'mapping/mapping.ttl',format='turtle')
    assert len(set(maps.subjects(RDF.type,rr.TriplesMap)))>=7


def make_db(tmp):
    db=tmp/'data.sqlite'
    with sqlite3.connect(db) as con:
        con.executescript((ROOT/'data/example.sql').read_text(encoding='utf-8'))
    return db


def test_sqlite_rdf_literal_zero_is_preserved(tmp_path):
    sys.path.insert(0,str(ROOT))
    from mapping.materialize import materialize
    db=make_db(tmp_path)
    out=tmp_path/'graph.nt'
    assert materialize(db,out)>700
    g=Graph().parse(out,format='nt')
    products=set(g.subjects(RDF.type,FS.PackagedProduct))
    assert len(products)==50
    assert sum(next(g.objects(p,FS.salt100g),None) is not None for p in products)==48
    assert sum(any(float(v)==0 for v in g.objects(p,FS.salt100g)) for p in products)==24


def test_invalid_energy_reaches_shacl_gate(tmp_path):
    sys.path.insert(0,str(ROOT))
    from mapping.materialize import materialize
    db=make_db(tmp_path)
    with sqlite3.connect(db) as con:
        con.execute('UPDATE off_products SET energy_kcal_100g=999 WHERE code=(SELECT code FROM off_products LIMIT 1)')
    out=tmp_path/'invalid.nt';materialize(db,out)
    g=Graph().parse(out,format='nt')
    assert any(float(v)==999 for v in g.objects(None,FS.energyKcal100g)), 'no pre-SHACL cleaning'
    pyshacl=pytest.importorskip('pyshacl')
    shapes=Graph().parse(ROOT/'shapes/shapes.ttl',format='turtle')
    ont=Graph().parse(ROOT/'ontology/foodsafe.ttl',format='turtle')
    ont.parse(ROOT/'ontology/foodon-slim.ttl',format='turtle')
    conforms,report,text=pyshacl.validate(data_graph=g,shacl_graph=shapes,ont_graph=ont,inference='rdfs',allow_warnings=True)
    assert not conforms
    assert 'energy' in text.lower()


def test_access_refuses_medical_and_scores_gold():
    sys.path.insert(0,str(ROOT/'access-layer'))
    import access_layer as a
    from score_utils import answer_set,set_f1
    graph=Graph().parse(ROOT/'build/graph.nt',format='nt')
    for ont in ['foodon-slim.ttl','foodsafe.ttl']:
        graph.parse(ROOT/'ontology'/ont,format='turtle')
    ex=a.load_examples()
    q='What is the safe medical dose of aspartame for a child eating this yogurt?'
    result=a.answer(q,graph,ex,mode='offline')
    assert result['refused'] and result['rows'] is None
    question='How many packaged products declare the gluten allergen?'
    result=a.answer(question,graph,ex,mode='offline')
    gold='SELECT (COUNT(?p) AS ?n) WHERE { ?p a foodsafe:PackagedProduct ; foodsafe:hasDeclaredAllergen foodsafe:AllergenGluten . }'
    assert result['rows'] and set_f1(answer_set(result['rows']),answer_set(a.run(graph,gold)))==1.0


def test_gnn_neighbor_information_changes_output():
    torch=pytest.importorskip('torch')
    sys.path.insert(0,str(ROOT/'model'))
    from gnn import SageLike
    model=SageLike(2,hidden=2)
    with torch.no_grad():
        model.lin_self.weight.zero_();model.lin_self.bias.zero_()
        model.lin_msg.weight.fill_(1);model.lin_msg.bias.zero_()
        model.out.weight.fill_(1);model.out.bias.zero_()
    x=torch.tensor([[1.,1.],[2.,2.]])
    edge=torch.tensor([[1],[0]])
    before=model(x,edge)[0,0].item()
    x[1]=torch.tensor([5.,5.])
    after=model(x,edge)[0,0].item()
    assert (before,after)==(8.,20.)
