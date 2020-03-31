import networkx as nx
import json
import rdflib
from pattern import Pattern
import testConstants as test
import queries
import matplotlib.pyplot as plt



def build_graph_with_st(st_path, ont_path, ld_path):
    source_graph = nx.MultiDiGraph()

    sts_json = read_sts_json(st_path)
    add_semantic_types(sts_json, source_graph)
    ontology = read_ontology(ont_path, 'turtle')
    LD_graph = read_ld(ld_path, 'turtle')

    # It is time consuming so use the test
    extract_patterns_unitary(LD_graph)
    #pattern_length_1 = extract_patterns_unitary_test(LD_graph)
    #build_longer_patterns(LD_graph, ontology, pattern_length_1, 2)

    return


def read_sts_json(st_path):
    """Loads the JSON formatted content of the file containing the
    semantic types of the source_graph
    
    Parameters
    ----------
    st_path : str
        The path to the file containing the semantic types
    
    Returns
    -------
    list
        The list of the objects inside the JSON file
    """

    f = open(st_path)
    sts = json.load(f)
    return sts


def add_semantic_types(sts, G):
    """Adds the semantic types returned by read_sts_json() to the
    directed graph passed as parameter
    
    Parameters
    ----------
    sts: list
        Loaded JSON containing semantic type information
    G: networkx.DiGraph
        Source graph (directed)
    
    Returns
    -------
    networkx.DiGraph
        The source graph with the newly added semantic types for each
        instance
    """

    sts = sts[0]
    attributes = sts['attributes']
    semantic_types = sts['semantic_types']

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


def read_ontology(ont_path, rdf_format):
    """Reads the file passed as argument as a triple-store containing
    the ontology information and builds a graph on its basis

    Parameters
    ----------
    ont_path : str
        The file containing the RDF triples building the ontology
    rdf_format : str
        Format description of the passed file (see rdflib.Graph.parse)

    Returns
    -------
    rdflib.Graph
        The graph containing the read ontology triples
    """
    
    f = open(ont_path, 'r')

    rdf_text = f.read()
    rdf_graph = rdflib.Graph()
    ontology = rdf_graph.parse(data=rdf_text, format=rdf_format)

    return ontology

def read_ld(ld_path, rdf_format):
    """Reads the file passed as argument as a triple-store containing
    the linked data information and builds a graph on its basis

    Parameters
    ----------
    ld_path : str
        The file containing the linked data triples
    rdf_format : str
        Format description of the passed file (see rdflib.Graph.parse)

    Returns
    -------
    rdflib.Graph
        The graph containing the read linked data triples
    """

    f = open(ld_path, 'r')

    rdf_text = f.read()
    rdf_graph = rdflib.Graph()
    ld_graph = rdf_graph.parse(data=rdf_text, format=rdf_format)

    return ld_graph


def extract_patterns_unitary(ld_graph: rdflib.Graph):
    """Extracts from the linked data graph the patterns of length 1 together
    with the instance nodes that are involved in such pattern.
    The information for each semantic relation is represented in a Pattern
    object.

    See the Pattern class docs for more details about the information handling.

    Parameters
    ----------
    ld_graph: rdflib.Graph
        The graph object containing the triples of the Linked data

    Returns
    -------
    list
        List of patterns (class Pattern) of length 1
    """
    
    qres = ld_graph.query(queries.length_1_triples)

    P1 = dict()
    i = 0
    for row in qres:
        (x, c1, p, y, c2) = row
        semantic_relation = (str(c1), str(p), str(c2))
        if semantic_relation not in P1.keys():
            # Create pattern graph and Pattern object
            new_g = nx.DiGraph()
            new_g.add_node(str(c1))
            new_g.add_node(str(c2))
            new_g.add_edge(str(c1), str(c2), property=str(p))
            new_p = Pattern(i, 1, new_g, 0)
            P1[semantic_relation] = new_p
            i += 1
        pattern = P1[semantic_relation]
        # Add to the classes of the pattern the according instances
        pattern.add_class_instance(str(c1), str(x))
        pattern.add_class_instance(str(c2), str(y))
        pattern.frequency += 1
    return list(P1.values())

# Only for test purposes (not updated yet)
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
    node_var_index = list()
    props = list()
    
    # Build query for old pattern
    print(pattern.p_graph.edges.data())
    for edge in pattern.p_graph.edges.data():
        if edge[0] not in node_var_index:
            node_var_index.append(edge[0])
            i1 = node_var_index.index(edge[0])
            query += f"\t?c{i1} rdf:type <{edge[0]}> .\n"
        if edge[1] not in node_var_index:
            node_var_index.append(edge[1])
            i2 = node_var_index.index(edge[1])
            query += f"\t?c{i2} rdf:type <{edge[1]}> .\n"
        prop = f"\t?c{i1} <{edge[2]['property']}> ?c{i2} .\n"
        props.append(prop) # This will be used later to avoid duplicate queries
        query += prop
        
    # Add to query the new part of the pattern to test
    new_edge = list(candidate.p_graph.edges.data())[0]
    if new_edge[0] not in node_var_index:
        node_var_index.append(new_edge[0])
        i1 = node_var_index.index(new_edge[0])
        query += f"\t?c{i1} rdf:type <{new_edge[0]}> .\n"
    if new_edge[1] not in node_var_index:
        node_var_index.append(new_edge[1])
        i2 = node_var_index.index(new_edge[1])
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
            for ont_class in [c for c in list(pattern.p_graph.nodes) if c in ont_classes]:
                P1_c = [p for p in length_1_patterns if p.p_graph.has_node(ont_class)]
                for p1_c in P1_c:
                    ask_for_link(ld_graph, pattern, p1_c, ont_class)



build_graph_with_st('./data/alaskaslist_st.json',
                    './data/ontology.ttl', './data/lod_example.rdf')
