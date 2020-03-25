import networkx as nx


class Pattern:
    def __init__(self, p_id: int, p_len: int, p_graph: nx.DiGraph, frequency: int):
        self.p_id = p_id
        self.p_len = p_len
        self.p_graph = p_graph
        self.frequency = frequency

    def __str__(self):
        return "id: " + str(self.p_id) + \
            "\nlength: " + str(self.p_len) + \
            "\nfrequency: " + str(self.frequency) + \
            "\nNodes of graph: " + str(list(self.p_graph.nodes)) + \
            "\nEdges of graph : " + str(list(self.p_graph.edges)) + "\n"
