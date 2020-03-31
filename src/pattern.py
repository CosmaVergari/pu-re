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
    
    The graph is exposed through the p_graph variable that is of type
    networkx.DiGraph and its handling has to be done externally.

    Additionally, Pttern objects can store the instances of each type that
    exist in the graph. This can be useful for the management of big graphs

    Attributes
    ----------
    p_id : int
        Unique id of pattern
    p_len : int
        Length of pattern
    p_graph : networkx.DiGraph
        Directed graph containing the semantic types and the properties
    frequency : int
        Number of repetitions of the pattern in the LD graph
    class_instances : dict
        key : str
            Semantic type in the graph
        value : list
            List of the instances of the semantic type in the LD graph
            that are involved in the pattern

    Methods
    -------
    add_class_instance(class_uri, instance_uri)
        Adds an instance to the list of instances of a specified class
    remove_class_instance(class_uri, instance_uri)
        Removes an instance from the list of instances of a specified class
    get_class_instances(class_uri)
        Returns the list of instances of a specified class
    """

    def __init__(self, p_id: int, p_len: int, p_graph: nx.DiGraph, frequency: int=0):
        """
        Parameters
        ----------
        p_id : int
            Unique id of pattern
        p_len : int
            Length of pattern
        p_graph : networkx.DiGraph
            Directed graph containing the semantic types and the properties
        frequency : int, optional
            Number of repetitions of the pattern in the LD graph (default is 0)
        """

        self.p_id = p_id
        self.p_len = p_len
        self.p_graph = p_graph
        self.frequency = frequency
        self.class_instances = dict()

    def add_class_instance(self, class_uri, instance_uri):
        """Adds an instance to the list of instances of a specified class

        Parameters
        ----------
        class_uri : str
            The uri of the class (semantic type)
        instance_uri : str
            The uri to be appended to the list of instances

        Raises
        ------
        ValueError
            If the class has not been added to the pattern graph before
            calling this method
        """

        if class_uri not in list(self.p_graph.nodes):
            raise ValueError(f"The class \"{class_uri}\" must be added to the pattern graph first")

        if class_uri not in self.class_instances.keys():
            self.class_instances[class_uri] = list()
            self.class_instances[class_uri].append(instance_uri)
        else:
            self.class_instances[class_uri].append(instance_uri)

    def remove_class_instance(self, class_uri, instance_uri):
        """Removes an instance from the list of instances of a specified class
        
        Parameters
        ----------
        class_uri : str
            The uri of the class (semantic type)
        instance_uri : str
            The uri to be removed from the list of instances

        Raises
        ------
        KeyError
            If the class has not been previously added or populated
        """

        if class_uri not in self.class_instances.keys():
            raise KeyError(f"There is no class named \"{class_uri}\"")
        else:
            self.class_instances[class_uri].remove(instance_uri)

    def get_class_instances(self, class_uri):
        """Returns the list of instances of a specified class
        
        Parameters
        ----------
        class_uri : str
            The uri of the class (semantic type) of interest
            
        Raises
        ------
        KeyError
            If the class has not been previously added or populated

        Returns
        -------
        list
            The list of the instances that are part of this pattern and
            are related to the specified class
        """

        if class_uri not in self.class_instances.keys():
            raise KeyError(f"There is no class named \"{class_uri}\"")
        else:
            return self.class_instances[class_uri]


    def __str__(self):
        return "id: " + str(self.p_id) + \
            "\nlength: " + str(self.p_len) + \
            "\nfrequency: " + str(self.frequency) + \
            "\nNodes of graph: " + str(list(self.p_graph.nodes)) + \
            "\nEdges of graph : " + str(self.p_graph.edges.data()) + "\n"
