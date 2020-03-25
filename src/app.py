import networkx as nx
import json
import rdflib
from pattern import Pattern
import testConstants as test


def build_graph_with_st(st_path, ont_path, ld_path):
    source_graph = nx.MultiDiGraph()

    sts_json = read_sts_json(st_path)
    add_semantic_types(sts_json, source_graph)
    ontology = read_ontology(ont_path)
    LD_graph = read_ld(ld_path)

    # It is time consuming so use the test
    # extract_patterns_unitary(LD_graph)
    pattern_length_1 = extract_patterns_unitary_test(LD_graph)
    build_longer_patterns(LD_graph, ontology, pattern_length_1, 2)

    return


def read_sts_json(st_path):
    f = open(st_path)
    sts = json.load(f)
    return sts


def add_semantic_types(sts, G):
    sts = sts[0]
    attributes = sts['attributes']
    semantic_types = sts['semantic_types']

    # TODO: if necessary, move here the code to create inverse edges

    for i in range(len(attributes)):

        # Add data nodes
        data_node = attributes[i]
        G.add_node(data_node,
                   type='attribute_name',
                   label=attributes[i])

        # Add class node
        class_node = semantic_types[i][0].split("***")[0]
        G.add_node(class_node,
                   type='class_uri',
                   label=class_node)

        # Set edge between a data node and a class node
        predicate = semantic_types[i][0].split('***')[1]
        G.add_edge(class_node, data_node,
                   key=class_node + '***' + predicate + '***' + data_node,
                   weight=1,
                   type='st_property_uri',
                   label=predicate,
                   name=class_node + '***' + data_node)

    return G


def read_ontology(ont_path):
    f = open(ont_path, 'r')

    rdf_text = f.read()
    rdf_graph = rdflib.Graph()
    ontology = rdf_graph.parse(data=rdf_text, format='turtle')

    return ontology

# def extract_ont_labels(ontology: rdflib.Graph):
#     qres = ontology.query("""SELECT ?c ?l
#                             WHERE { ?c rdfs:label ?l }""")
#     d = dict()
#     for row in qres:
#         d[row.c] = row.l
#     return d


def read_ld(ld_path):
    f = open(ld_path, 'r')

    rdf_text = f.read()
    rdf_graph = rdflib.Graph()
    ld_graph = rdf_graph.parse(data=rdf_text, format='turtle')

    return ld_graph


def extract_patterns_unitary(ld_graph: rdflib.Graph):
    qres = ld_graph.query("""SELECT DISTINCT ?c1 ?p ?c2 (COUNT(*) as ?cnt)
                            WHERE { ?x ?p ?y. ?x rdf:type ?c1. ?y rdf:type ?c2. }
                            GROUP BY ?c1 ?p ?c2""")

    i = 0
    P1 = []
    for row in qres:
        new_g = nx.DiGraph()
        new_g.add_node(str(row.c1))
        new_g.add_node(str(row.c2))
        new_g.add_edge(str(row.c1), str(row.c2), property=str(row.p))
        P1.append(Pattern(i, 1, new_g, int(str(row.cnt))))
        i += 1
    return P1

# Only for test purposes


def extract_patterns_unitary_test(ld_graph):
    P1 = []
    i = 0
    for row in test.P1:
        new_g = nx.DiGraph()
        new_g.add_node(str(row[0]))
        new_g.add_node(str(row[2]))
        new_g.add_edge(str(row[0]), str(row[2]), property=str(row[1]))
        new_p = Pattern(i, 1, new_g, int(str(row[3])))
        P1.append(new_p)
        i += 1
    return P1

def extract_ontology_classes(ontology: rdflib.Graph):
    qres = ontology.query("""SELECT ?c
                            WHERE { ?c rdf:type rdfs:Class }""")
    return [str(res[0]) for res in qres]


def build_longer_patterns(ld_graph, ontology, length_1_patterns, max_len: int):
    P = dict()
    P[1] = length_1_patterns;
    p_id = len(length_1_patterns)
    i = 1
    ont_classes = extract_ontology_classes(ontology)
    while (i < max_len):
        for pattern1 in P[i]:
            # TODO : Unique identifier for each node in the pattern graph
            # Because there might be more than 1 classes with same URI
            for ont_class in [c for c in list(pattern1.p_graph.nodes) if ont_classes.count(c) == 1]:
                P1_c = [p for p in length_1_patterns if p.p_graph.has_node(ont_class)]
                for p1_c in P1_c:
                    pass


build_graph_with_st('./data/alaskaslist_st.json',
                    './data/ontology.ttl', './data/lod_example.rdf')
