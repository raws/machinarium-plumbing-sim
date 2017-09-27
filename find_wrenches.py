import csv
import itertools


class Node:
    def __init__(self, name):
        self.neighbors = set()
        self.name = name


class Graph:
    def __init__(self, nodes=dict(), adjacency_matrix_path=None, edges=None):
        self.nodes = nodes
        if adjacency_matrix_path:
            self.import_adj_matrix_csv(adjacency_matrix_path)
        if edges:
            self.add_edges(edges)

    def add_nodes(self, nodes_list):
        """
        Takes list of new node names, adds to self.nodes.
        :param nodes_list: (list) list of node names
        """
        node_dict = {name: Node(name) for name in nodes_list}
        if self.nodes:
            self.nodes.update(node_dict)
        else:
            self.nodes = node_dict

    def add_edge(self, edge_pair):
        """
        For pair of nodes (a,b) representing an edge, adds a as a neighbor of b and b as a neighbor of a
        :param edge_pair: (list or tuple) of two nodes that share an edge
        """
        self.nodes[edge_pair[0]].neighbors.add(edge_pair[1])
        self.nodes[edge_pair[1]].neighbors.add(edge_pair[0])

    def add_edges(self, edge_pairs):
        """
        For each in list of node pairs [(a,b), ... , (c,d)], adds the edge it represents
        :param edge_pairs: (list) of pairs of nodes that share an edge
        """
        for edge in edge_pairs:
            self.add_edge(edge)

    def delete_edge(self, edge):
        """
        For pair of nodes (a,b) representing an edge, removes a from neighbors of b and b from neighbors of a
        :param edge: (list or tuple) of two nodes that share an edge
        """
        self.nodes[edge[0]].neighbors.discard(edge[1])
        self.nodes[edge[1]].neighbors.discard(edge[0])

    def delete_edges(self, edge_pairs):
        """
        For each in list of node pairs [(a,b), ... , (c,d)], removes the edge it represents
        :param edge_pairs: (list) of pairs of nodes whose edges are to be removed
        :return:
        """
        for edge in edge_pairs:
            self.delete_edge(edge)

    def import_adj_matrix_csv(self, csv_file_path):
        """
        Imports nodes and edges from an adjacency matrix stored as a csv.

        The first column of the matrix is a list of the names of all of the nodes of the graph. After the first row,
        each row of the matrix is a list representing a node. The name of the node is extracted from the first element
        of the list representing that row. Each column corresponds to a potential neighbor of that node. If the entry
        for that column is 1, then that row-column pair is added as an edge.

        :param csv_file_path: (string) of filepath leading to csv of adjacency matrix representing the graph
        """
        with open(csv_file_path) as csv_file:
            # create an iterator of the rows in the csv file
            adjacency_matrix = csv.reader(csv_file)
            # set the first row of the csv as the index to refer to for the neighbors of subsequent rows
            column_names = adjacency_matrix.__next__()
            # add all non-empty nodes named in the index to the graph
            self.add_nodes([node for node in column_names if node != ''])
            # each row in the csv represents a node. from this row, collect information about that node's neighbors
            for row in adjacency_matrix:
                # the node name is the first element in the row
                node = row[0]
                c = 0  # initiate column index
                for element in row:
                    if element == '1':
                        self.add_edge([node, column_names[c]])
                    c += 1

    def get_node_neighbor_list(self):
        """
        Prints the name of each node in the graph as well as its associated neighbors
        """
        for node_name in self.nodes:
            print('node: ' + node_name + ' , neighbors: ' + str(g.nodes[node_name].neighbors))

    def path_exists(self, root, target):
        """
        Checks whether a path exists between the root and target nodes.

        Iteratively generates a list of all nodes that are in the same connected component as the root node. If the
        target node is in the root's component, returns True. Once all neighbors of all nodes in the component have
        been added, if the target node is not in the component list, returns False.

        :param root: (string) nome of root node
        :param target: (string) name of target node
        :returns: True or False
        """
        # initiate the component list by adding all of the neighbors of the root node to the component
        component = [each for each in self.nodes[root].neighbors]
        # once i == length of the component list, all current nodes in the component have been considered and all of
        # their neighbors are already accounted for in the component list
        i = 0
        while i < len(component):
            node_name = component[i]
            node = self.nodes[node_name]
            # add all new neighbors found to the end of the component list
            component += [each for each in node.neighbors if each not in component]
            i += 1
            if target in component:
                return True
        return False


class PipeGraph(Graph):
    """
    A PipeGraph represents the type of graph we need to solve the Machinarium pipe problem. We have a root node
    representing a water source, a target node representing the pipe from which we want to cut off the flow of water,
    and edges we can delete from the graph representing intermediate pipe segments through which we can cut off the flow
    of water using wrenches, of which we have three.
    """
    def __init__(self, nodes=dict(), adjacency_matrix_path=None, edges=None,
                 wrenchable_edges = dict(), root=None, target=None):
        Graph.__init__(self, nodes, adjacency_matrix_path, edges)
        self.wrenchable_edges = wrenchable_edges
        self.root = root
        self.target = target

    def find_wrench_edges(self):
        """
        Locates the three edges in the graph that will cut off flow from the root node to the target node if they are
        wrenched. Assumes a unique solution.
        :return: list of three edges, or if no solution, None
        """
        for three_edge_combo in itertools.combinations(self.wrenchable_edges, 3):
            self.delete_edges(three_edge_combo)
            if not self.path_exists(self.root, self.target):
                return [self.wrenchable_edges[edge] for edge in three_edge_combo]
            self.add_edges(three_edge_combo)
        return None


if __name__ == '__main__':
    g = PipeGraph(adjacency_matrix_path='machinarium/adjacency_matrix.csv',
                  root='a1', target='d9')
    g.get_node_neighbor_list()
    g.wrenchable_edges = {('c3', 'c1'): 'c2',
                          ('b5', 'b1'): 'b2',
                          ('d4', 'c4'): 'd2',
                          ('f4', 'e3'): 'f2',
                          ('b7', 'b5'): 'b6',
                          ('c7', 'c4'): 'c6',
                          ('e7', 'e4'): 'e6',
                          ('h7', 'g1'): 'h6',
                          ('d7', 'd4'): 'd6',
                          ('g9', 'f4'): 'f6'}
    print(g.find_wrench_edges())

