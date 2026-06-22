"""Extract FoodOn OWL classes into neutral, provenance-preserving staging records."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from rdflib import Graph, OWL, RDF, RDFS, URIRef

FOODON_IRI_PREFIX = "http://purl.obolibrary.org/obo/FOODON_"
OBOINOWL = "http://www.geneontology.org/formats/oboInOwl#"
SYNONYM_PREDICATES = (
    URIRef(OBOINOWL + "hasExactSynonym"),
    URIRef(OBOINOWL + "hasRelatedSynonym"),
    URIRef(OBOINOWL + "hasBroadSynonym"),
    URIRef(OBOINOWL + "hasNarrowSynonym"),
)
DEFINITION_PREDICATE = URIRef(OBOINOWL + "hasDefinition")


def foodon_id(iri: URIRef) -> str:
    return "FOODON:" + str(iri).removeprefix(FOODON_IRI_PREFIX)


def is_foodon_iri(value: object) -> bool:
    return isinstance(value, URIRef) and str(value).startswith(FOODON_IRI_PREFIX)


def extract_foodon_classes(graph: Graph, raw_file: str, retrieved_at: str) -> Iterator[dict[str, object]]:
    """Yield direct FoodOn classes only; imported external ontology classes are excluded."""
    classes = sorted(
        {subject for subject in graph.subjects(RDF.type, OWL.Class) if is_foodon_iri(subject)},
        key=str,
    )
    for class_iri in classes:
        label = next(graph.objects(class_iri, RDFS.label), None)
        if label is None:
            continue
        parents = sorted(
            foodon_id(parent)
            for parent in graph.objects(class_iri, RDFS.subClassOf)
            if is_foodon_iri(parent)
        )
        synonyms = sorted({str(value) for predicate in SYNONYM_PREDICATES for value in graph.objects(class_iri, predicate)})
        definition = next(graph.objects(class_iri, DEFINITION_PREDICATE), None)
        yield {
            "source_iri": str(class_iri),
            "source_foodon_id": foodon_id(class_iri),
            "label": str(label),
            "definition": str(definition) if definition else None,
            "synonyms": synonyms,
            "parent_foodon_ids": parents,
            "source_id": "SOURCE:FOODON",
            "source_url": "https://github.com/FoodOntology/foodon",
            "raw_file": raw_file,
            "retrieved_at": retrieved_at,
        }


def extract(owl_file: Path, output_file: Path, retrieved_at: str | None = None) -> int:
    retrieved_at = retrieved_at or datetime.now(UTC).date().isoformat()
    graph = Graph()
    graph.parse(owl_file, format="xml")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_file.open("w", encoding="utf-8") as output:
        for record in extract_foodon_classes(graph, owl_file.name, retrieved_at):
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract FoodOn OWL classes into staging JSONL")
    parser.add_argument("--owl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at", help="ISO date; defaults to today's UTC date")
    args = parser.parse_args()
    count = extract(args.owl, args.output, args.retrieved_at)
    print(f"Extracted {count} FoodOn classes to {args.output}")


if __name__ == "__main__":
    main()
