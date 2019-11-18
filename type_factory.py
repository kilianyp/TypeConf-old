"""This works sequentially by performing first a dependency analysis"""

from dep_graph import DependencyGraph
import utils as u
import logging
from base_types import BASE_TYPES
from attribute import AttributeFactory
from base_types import Descriptor
import json

MAGIC_SPLIT_NAME = '.'

logger = logging.getLogger()


class Config(dict):
    """ TODO access per dot.
        print with help"""
    def __str__(self):
        return json.dumps(self, indent=4)


class OneOf(Descriptor):
    """
    One Of value
    """
    def __init__(self, name):
        super().__init__(name)
        self.options = set()

    def parse(self):
        if self.value not in self.options:
            raise ValueError("Expected a value from {}. Got {}.".format(self, self.value))
        return True

    def add_option(self, option):
        self.options.add(option)

    def add_options(self, options):
        for option in options:
            self.add_option(option)

    def __str__(self):
        return ', '.join(str(o) for o in self.options)


class Const(Descriptor):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        raise ValueError("{} is const, cannot set value {}".format(self.name, value))

    def __init__(self, name, value):
        super().__init__(name)
        self._value = value
        self.isset = True

    def parse(self):
        return True


class OneOfType(Descriptor):
    """
    One of Type
    MasterType:
        SubType:
            a1: 0
    """
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # for now set all subtypes even though only one allowed
        if len(value.keys()) == 0:
            raise ValueError("{}: There are no keys in {}".format(self.name, value))
        # only set when we have atleast one value
        self._value = value
        self.isset = True
        for k, v in value.items():
            if k not in self.subtypes:
                raise ValueError("Unknown type {} in {}. Choose from {}.".format(k, self.name, str(self.subtypes.keys())))
            self.subtypes[k].value = v

    def __init__(self, name, subtypes):
        super().__init__(name)
        assert len(subtypes) > 0, "At least on subtype is necessary"
        self.subtypes = subtypes

    def parse(self):
        if len(self.value.keys()) > 1:
            raise ValueError("Choose only one from")

        sub = list(self.value.keys())[0]
        sub = self.subtypes[sub]
        return sub.parse()

    def to_config(self):
        subkey = list(self.value.keys())[0]
        sub = self.subtypes[subkey]
        return {subkey: sub.to_config()}


class MultipleOfType(Descriptor):
    """
    Multiple of Type
    MasterType:
        SubType1:
            a1: 0
        SubType2:
            a1: 0
    """
    def __init__(self, name):
        super().__init__(name)
        raise NotImplementedError()

# TODO parsing is spread between building, value setting and parse function
# TODO try to do everything in parse

class CompositeType(Descriptor):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.isset = True
        """
        Sets all the attribute values
        TODO what happens if not in cache
        TODO what about cycles
        """
        # assert that this is a mapping
        print(self.name, value)
        for key, attribute in self.attributes.items():
            # if no value for attribute
            if key not in value:
                continue
            attribute.descriptor.value = value.pop(key)

        if len(value) != 0:
            logger.warning("There are unused keys in this config: %s", ", ".join(value.keys()))

    def __init__(self, name):
        super().__init__(name)
        self.attributes = {}

    def __str__(self):
        string = "{} with {} attributes\n".format(self.name, len(self.attributes))
        for key, attribute in self.attributes.items():
            string += "{}: {}\n".format(key, attribute)
        # remove last new line
        string = string[:-1]
        return string

    def add_attribute(self, name, attribute):
        if name in self.attributes:
            raise KeyError("Attribute with key {} already exists".format(name))
        self.attributes[name] = attribute

    def parse(self):
        # TODO
        is_valid = True
        for key, attribute in self.attributes.items():
            try:
                attribute.parse()
            except ValueError as e:
                print(key, attribute.descriptor.value)
                raise
        return is_valid

    def __len__(self):
        return len(self.attributes)

    def to_config(self):
        return Config({key: attribute.descriptor.to_config() for key, attribute in self.attributes.items()})


class FileTree(object):
    """
    A simple to keep track of the subclasses of a folder
    """
    def __init__(self):
        self.nested = {}

    def add(self, structure, name):
        """This does not work
        if a directory is added before the file.
        """
        level = self.nested
        for s in structure[:-1]:
            if s not in level:
                level[s] = {}
            level = level[s]
        level[structure[-1]] = name

    def get(self, structure):
        level = self.nested
        for s in structure:
            level = level[s]
        return level.values()


class TypeFactory(object):
    def __init__(self):
        self.types = {}
        self.dependency_graph = DependencyGraph()
        self.file_tree = FileTree()
        for name, typ in BASE_TYPES.items():
            self.register_type(name, typ(name))

    def register_search_directory(self, path):
        for path, structure, type_enum in u.discover(path):
            name = MAGIC_SPLIT_NAME.join(structure)
            if type_enum == u.FILE_ENUM:
                self.register_file(name, path, structure)
            elif type_enum == u.DIR_ENUM:
                self.register_directory(name, path, structure)
            else:
                raise ValueError("Unknown type {}".format(type_enum))

    def register_directory(self, name, path, structure):
        # TODO dependencies are not set correctly
        # it must be ensured that all directory subtypes are alread processed
        # cfg is None if it is a folder
        dependencies = self.file_tree.get(structure)
        self.dependency_graph.add(name, None, set(dependencies))

    def register_file(self, name, path, structure):
        cfg = u.read_file(path)
        if cfg is None:
            logger.warning("Skipping %s (%s)", name, path)

        self.file_tree.add(structure, name)
        self.register_cfg(name, cfg)

    def register_type(self, name, type):
        self.types[name] = type
        # making this type available
        self.dependency_graph.add(name)

    def register_cfg(self, name, cfg):
        dependencies = self.extract_dependcies(cfg)
        self.dependency_graph.add(name, cfg, dependencies)

    def build(self, name):
        build_order = self.dependency_graph.get_dep_order(name)
        for type_name in build_order:
            node = self.dependency_graph.get_node(name)
            if node.name in self.types:
                continue
            self.types[node.name] = self.build_from_node(node)
        return self.types[name]

    def build_type(self, type, name, cfg):
        if type == "oneof":
            descriptor = OneOf(name)
            descriptor.add_options(cfg.pop('options'))
        elif type == "datatype":
            # this type exists because of dependency analysis
            descriptor = self.get(cfg.pop('dtype'))
        elif type == "const":
            descriptor = Const(name, cfg.pop('value'))
        elif type == "one_of_type":
            # Folder
            subtypes = {}
            for dep in cfg['subtypes']:
                subtypes[dep] = self.get(dep)
            descriptor = OneOfType(name, subtypes)
        elif type == "composite_type":
            descriptor = CompositeType(name)
            for key, values in cfg.items():
                try:
                    type_name = values.pop('type')
                    type = self.build_type(type_name, key, values)
                    attribute = AttributeFactory.build(key, type, values)
                except:
                    print(key, values, name)
                    raise
                descriptor.add_attribute(key, attribute)
            # TODO differentiate between errors in templates and config
        else:
            raise ValueError("Error in Template {}: unknown type {}".format(name, type))
        return descriptor

    def build_from_node(self, node):
        cfg = node.cfg
        if cfg is None:
            cfg = {'subtypes': node.dependency_list}
            type_name = "one_of_type"
        else:
            type_name = "composite_type"
        return self.build_type(type_name, node.name, cfg)

    def get(self, name):
        import copy
        if name not in self.types:
            typ = self.build(name)
        else:
            typ = self.types[name]

        return copy.deepcopy(typ)

    @staticmethod
    def extract_dependcies(cfg):
        dependencies = set()
        for key, value in cfg.items():
            if value['type'] == 'datatype':
                dependencies.add(value['dtype'])
        return dependencies
