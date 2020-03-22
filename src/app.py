import networkx as nx
import json
import rdflib


def build_graph_with_st(st_path, ont_path, ld_path):
    source_graph = nx.MultiDiGraph()

    sts_json = read_sts_json(st_path)
    add_semantic_types(sts_json, source_graph)
    ontology = read_ontology(ont_path)
    LD_graph = read_ld(ld_path)
    extract_patterns_unitary(LD_graph)

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

def read_ld(ld_path):
    f = open(ld_path, 'r')

    rdf_text = f.read()
    rdf_graph = rdflib.Graph()
    ld_graph = rdf_graph.parse(data=rdf_text, format='turtle')

    return ld_graph

def extract_patterns_unitary(ld_graph: rdflib.Graph):
    qres = ld_graph.query("""SELECT DISTINCT ?c1 ?p ?c2 (COUNT(*) as ?count)
                            WHERE { ?x ?p ?y. ?x rdf:type ?c1. ?y rdf:type ?c2. }
                            GROUP BY ?c1 ?p ?c2""")
    for row in qres:
        print(row)

build_graph_with_st('./data/alaskaslist_st.json', './data/ontology.ttl', './data/lod_example.rdf')