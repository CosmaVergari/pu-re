import networkx as nx

class Pattern:
    """
    A class that represents a pattern of variable length.
    A pattern is intended as a set of relations between semantic types.
    The information about such relations are stored in a directed graph
    similar to the following:

    c1 : class 1 (graph node)
    c2 : class 2 (graph node)
    p : property that links classes 1 and 2 (graph edge)

                c1 --p--> c2
    
    The graph is exposed through the class_graph variable that is of type
    networkx.DiGraph and its handling has to be done externally.

    Additionally, Pattern objects can store the instances of each type that
    exist in the graph. This can be useful for the management of big graphs

    Attributes
    ----------
    p_id : int
        Unique id of pattern
    p_len : int
        Length of pattern
    class_graph : networkx.DiGraph
        Directed graph containing the semantic types and the properties
    frequency : int
        Number of repetitions of the pattern in the LD graph
    instances_graph : networkx.DiGraph
        Directed graph containing the instances for each class connected
        with same properties shown in class_graph
    """

    def __init__(self, p_id: int, p_len: int, frequency: int=0):
        """
        Parameters
        ----------
        p_id : int
            Unique id of pattern
        p_len : int
            Length of pattern
        class_graph : networkx.DiGraph
            Directed graph containing the semantic types and the properties
        frequency : int, optional
            Number of repetitions of the pattern in the LD graph (default is 0)
        """

        self.p_id = p_id
        self.p_len = p_len
        self.class_graph = nx.DiGraph()
        self.frequency = frequency
        self.instances_graph = nx.DiGraph()

    
    def add_relation(self, class_1, class_2, relation):
        if class_1 not in list(self.class_graph.nodes):
            self.class_graph.add_node(class_1, type="class")
        if class_2 not in list(self.class_graph.nodes):
            self.class_graph.add_node(class_2, type="class")
        self.class_graph.add_edge(class_1, class_2, property=relation)

    def add_relation_instance(self, class_1, instance_1, class_2, instance_2, relation):
        if (class_1 not in list(self.class_graph.nodes)) or (class_2 not in list(self.class_graph.nodes)):
            raise ValueError("Both classes must be added to the semantic relation graph first")

        if instance_1 not in list(self.instances_graph.nodes):
            self.instances_graph.add_node(instance_1, type="instance", instanceof=class_1)
        if instance_2 not in list(self.instances_graph.nodes):
            self.instances_graph.add_node(instance_2, type="instance", instanceof=class_2)
        self.instances_graph.add_edge(instance_1, instance_2, property=relation)

    def get_classes(self):
        return list(self.class_graph.nodes)

    #def get_instances(self, class_1):
        #self.instances_graph.predecessors()

    def __str__(self):
        return "id: " + str(self.p_id) + \
            "\nlength: " + str(self.p_len) + \
            "\nfrequency: " + str(self.frequency) + \
            "\nNodes of graph: " + str(list(self.class_graph.nodes)) + \
            "\nEdges of graph : " + str(self.class_graph.edges.data()) + "\n"