from rdflib import Graph

from food_kg.extractors.foodon import extract_foodon_classes


def test_extracts_only_foodon_classes_and_direct_parents() -> None:
    graph = Graph()
    graph.parse(data='''
      @prefix owl: <http://www.w3.org/2002/07/owl#> .
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
      @prefix obo: <http://purl.obolibrary.org/obo/> .
      @prefix oio: <http://www.geneontology.org/formats/oboInOwl#> .
      obo:FOODON_0001 a owl:Class ; rdfs:label "food material" .
      obo:FOODON_0002 a owl:Class ; rdfs:label "rice flour" ;
        rdfs:subClassOf obo:FOODON_0001 ;
        oio:hasExactSynonym "rice powder" .
      obo:CHEBI_123 a owl:Class ; rdfs:label "external chemical" .
    ''', format="turtle")
    records = list(extract_foodon_classes(graph, "foodon.owl", "2026-06-22"))
    assert [record["source_foodon_id"] for record in records] == ["FOODON:0001", "FOODON:0002"]
    assert records[1]["parent_foodon_ids"] == ["FOODON:0001"]
    assert records[1]["synonyms"] == ["rice powder"]
