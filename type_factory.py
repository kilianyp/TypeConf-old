"""This works sequentially by performing first a dependency analysis"""

from dep_graph import DependencyGraph
import utils as u
import logging
from base_types import BASE_TYPES

logger = logging.getLogger()


class TypeCache(object):
    def __init__(self):
        self._cache = {}

    def __setitem__(self, key, value):
        cache_level = self._cache
        key_levels = key.split(u.MAGIC_SPLIT_NAME)
        if len(key_levels) > 1:
            # create structure until the last one
            for p in key_levels[:-1]:
                # ASSERT cache level is cache
                if p not in cache_level:
                    cache_level[p] = {}
                cache_level = cache_level[p]
            key = key_levels[-1]
        cache_level[key] = value

    def __getitem__(self, key):
        # TODO nested folders as in set item
        return self._cache[key]

    def __contains__(self, item):
        return item in self._cache

    def __str__(self):
        string = "{} Elements in cache\n".format(len(self._cache))
        for key, descriptor in self._cache.items():
            string += "{}: {}\n".format(key, descriptor)
        string += "a"
        return string


class TypeFactory(object):
    def __init__(self):
        self.types = TypeCache()
        self.dependency_graph = DependencyGraph()
        for name, typ in BASE_TYPES.items():
            self.register_type(name, typ(name))

    def register_search_directory(self, path):
        for path, name, type_enum in u.discover(path):
            if type_enum == u.FILE_ENUM:
                self.register_file(name, path)
            elif type_enum == u.DIR_ENUM:
                self.register_directory(name, path)
            else:
                raise ValueError("Unknown type {}".format(type_enum))

    def register_type(self, name, type):
        self.types[name] = type
        # making this type available
        self.dependency_graph.add(name)

    def register_cfg(self, name, cfg):
        dependencies = self.extract_dependcies(cfg)
        self.dependency_graph.add(name, cfg, dependencies)

    def register_directory(self, name, path):
        # TODO dependencies are not set correctly
        raise NotImplementedError
        self.dependency_graph.add(name, {}, set())

    def register_file(self, name, path):
        cfg = u.read_file(path)
        if cfg is None:
            logger.warning("Skipping %s (%s)", name, path)
            return
        self.register_cfg(name, cfg)

    def build_type(self, name):
        build_order = self.dependency_graph.get_dep_order(name)
        for type_name in build_order:
            node = self.dependency_graph.get_node(name)
            if node.name in self.types:
                continue

            self.types[node.name] = self.build_from_node(node)
        return self.types[name]

    def build_from_node(self, node):
        return node

    @staticmethod
    def extract_dependcies(cfg):
        dependencies = set()
        for key, value in cfg.items():
            if value['type'] == 'datatype':
                dependencies.add(value['dtype'])
        return dependencies
