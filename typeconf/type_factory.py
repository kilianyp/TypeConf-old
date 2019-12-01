"""This works sequentially by performing first a dependency analysis"""

import logging
import json
import os
from .dep_graph import DependencyGraph
from .file_tree import FileTree
from . import utils as u
from .parser import BASE_TYPES, Parser
from .attribute import AttributeFactory
from .config_template import ConfigTemplate

MAGIC_SPLIT_NAME = '.'

logger = logging.getLogger()


class Config(dict):
    """ TODO access per dot.
        print with help"""
    def __str__(self):
        return json.dumps(self, indent=4)


class OneOf(Parser):
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


class Const(Parser):
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


class OneOfType(Parser):
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


class MultipleOfType(Parser):
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

class CompositeType(Parser):
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
        for key, attribute in self.attributes.items():
            # if no value for attribute
            if key not in value:
                continue
            attribute.parser.value = value.pop(key)

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
                print(key, attribute.parser.value)
                raise
        return is_valid

    def __len__(self):
        return len(self.attributes)

    def to_config(self):
        return Config({key: attribute.parser.to_config() for key, attribute in self.attributes.items()})


class FileType(Parser):
    def __init__(self, name, overwrite=False, make_path=True):
        self.__init__(name)
        self.overwrite = overwrite
        self.make_path = make_path

    def parse(self):
        if os.path.isfile(self.value):
            if self.overwrite:
                return True
            else:
                return False
        if self.value.endswith(os.path.sep):
            raise ValueError("Passed a folder")
            return False
        if os.path.isdir(self.value):
            raise ValueError("A Folder with this name exits")
            return False
        path = os.path.dirname(self.value)
        if self.make_path:
            u.make_path(path)
            return True
        else:
            raise ValueError(f"Path {self.value} does not exist and"
                             "was not created")


class FolderType(Parser):
    def __init__(self, make_path=True):
        self.make_path = path
    def parse(self):
        if os.path.isdir(self.value):
            return True
        if os.path.isfile(path):
            raise ValueError("Is File")
            return False

        if self.make_path:
            os.makedirs(self.value)
            return True
        raise ValueError("Path does not exist and was not created")
        return False


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

        self.file_tree.add(name, structure)
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
            parser = OneOf(name)
            parser.add_options(cfg.pop('options'))
        elif type == "datatype":
            # this type exists because of dependency analysis
            parser = self.get(cfg.pop('dtype'))
        elif type == "const":
            parser = Const(name, cfg.pop('value'))
        elif type == "one_of_type":
            # Folder
            subtypes = {}
            for dep in cfg['subtypes']:
                subtypes[dep] = self.get(dep)
            parser = OneOfType(name, subtypes)
        elif type == "composite_type":
            parser = CompositeType(name)
            for key, values in cfg.items():
                try:
                    type_name = values.pop('type')
                    type = self.build_type(type_name, key, values)
                    attribute = AttributeFactory.build(key, type, values)
                except:
                    print(key, values, name)
                    raise
                parser.add_attribute(key, attribute)
            # TODO differentiate between errors in templates and config
        else:
            raise ValueError("Error in Template {}: unknown type {}".format(name, type))
        return parser

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

    def build_template(self, name):
        return ConfigTemplate(name, self.get(name))

    @staticmethod
    def extract_dependcies(cfg):
        dependencies = set()
        for key, value in cfg.items():
            if value['type'] == 'datatype':
                dependencies.add(value['dtype'])
        return dependencies
