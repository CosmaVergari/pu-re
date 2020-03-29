import networkx as nx
import json
import rdflib
from pattern import Pattern
from copy import deepcopy
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
    qres = ontology.query("""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?c
    WHERE { ?c rdf:type rdfs:Class }""")
    return [str(res[0]) for res in qres]

def ask_for_link(ld_graph: rdflib.Graph, pattern: Pattern, candidate: Pattern, ont_class: str):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
ASK WHERE { """
    i = 0

    # Build a node<->variable_name association for query variables
    node_var__ = list()
    props = list()
    
    # Build query for old pattern
    for edge in pattern.p_graph.edges.data():
        if edge[0] not in node_var__:
            node_var__.append(edge[0])
        i1 = node_var__.index(edge[0])
        query += f"\t?c{i1} rdf:type <{edge[0]}> .\n"
        if edge[1] not in node_var__:
            node_var__.append(edge[1])
        i2 = node_var__.index(edge[1])
        query += f"\t?c{i2} rdf:type <{edge[1]}> .\n"
        prop = f"\t?c{i1} <{edge[2]['property']}> ?c{i2} .\n"
        props.append(prop) # This will be used later to avoid duplicate queries
        query += prop
        
    # Add to query the new part of the pattern to test
    new_edge = list(candidate.p_graph.edges.data())[0]
    if new_edge[0] not in node_var__:
        node_var__.append(new_edge[0])
    i1 = node_var__.index(new_edge[0])
    query += f"\t?c{i1} rdf:type <{new_edge[0]}> .\n"
    if new_edge[1] not in node_var__:
        node_var__.append(new_edge[1])
    i2 = node_var__.index(new_edge[1])
    query += f"\t?c{i2} rdf:type <{new_edge[1]}> .\n"
    prop = f"\t?c{i1} <{new_edge[2]['property']}> ?c{i2} .\n"
    # Check if the same property has been added elsewhere in the query (see comment above)
    if prop in props:
        return -1
    query += prop + " }"
    print(query)

    # Query the LD graph
    qres = ld_graph.query(query)
    for row in qres:
        print(row)
        return row

def build_longer_patterns(ld_graph, ontology, length_1_patterns, max_len: int):
    P = dict()
    P[1] = length_1_patterns
    p_id = len(length_1_patterns)
    i = 1
    ont_classes = extract_ontology_classes(ontology)
    while (i < max_len):
        for pattern in P[i]:
            for ont_class in [c for c in list(pattern.p_graph.nodes) if ont_classes.count(c) == 1]:
                P1_c = [p for p in length_1_patterns if p.p_graph.has_node(ont_class)]
                for p1_c in P1_c:
                    ask_for_link(ld_graph, pattern, p1_c, ont_class)



build_graph_with_st('./data/alaskaslist_st.json',
                    './data/ontology.ttl', './data/lod_example.rdf')
