class OrderedSet(dict):
    def add(self, elem):
        self[elem] = None

    def union(self, elems):
        for e in elems:
            self.add(e)


class TypeNode(object):
    def __init__(self, name, cfg=None, dependency_list=set()):
        """
        Args:
        dependencies: list of DependencyNodes
        """
        self.dependency_list = dependency_list
        self.name = name
        self.cfg = cfg


class DependencyGraph(object):
    def __init__(self):
        self.types = {}

    def add_node(self, node):
        self.types[node.name] = node

    def add(self, *args, **kwargs):
        self.add_node(TypeNode(*args, **kwargs))

    def get_node(self, name):
        return self.types[name]

    def get_dep_order(self, name, parents=set()):
        # we need a unique copy for this level
        parents = parents.copy()
        if name not in self.types:
            raise ValueError("Unknown type {}. Required by one of {}".format(name, parents))
        node = self.types[name]

        if name in parents:
            raise ValueError("Cycle", name, parents)

        parents.add(name)
        ordered_deps = OrderedSet()
        for dep in node.dependency_list:
            ordered_deps.union(self.get_dep_order(dep, parents))

        ordered_deps.union(node.dependency_list)
        return ordered_deps


if __name__ == "__main__":
    graph = DependencyGraph()
    node1 = TypeNode("a", ["b", "c", "d"])
    node2 = TypeNode("b", ["c"])
    node3 = TypeNode("c", ["d"])
    node4 = TypeNode("d", ["b"])

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)

    print(graph.get_dep_order("a"))
