import os
import logging

logger = logging.getLogger()
SUPPORTED_FILETYPES = ['.yaml', '.json']
IGNORE = ["__pycache__", './']
DEFAULT_DESCRIPTOR_PATH = 'protos'


def discover(basepath=DEFAULT_DESCRIPTOR_PATH, prefix=''):
    """
    Recursively check for supported files
    we need to first build the ones without dependencies, which are in the subfolders,
    descriptors on the same level cannot depend on each other
    we do this by seeing the folder structure hierachically
    TODO
    first subfolders before files
    files in subfolders before subfolder
    """
    for f in os.listdir(basepath):
        if f in IGNORE:
            continue

        path = os.path.join(basepath, f)

        if os.path.isdir(path):
            for returnvalue in discover(path, prefix + f + '.'):
                yield returnvalue
            yield path, prefix + f
        elif os.path.isfile(path):
            for ftype in SUPPORTED_FILETYPES:
                if f.endswith(ftype):
                    yield path, prefix + f.rstrip(ftype)
                    break
        else:
            raise RuntimeError("Not supported case TODO")


class Cache(object):
    def __init__(self):
        self._cache = {}

    def __setitem__(self, key, value):
        self._cache[key] = value

    def __getitem__(self, key):
        return self._cache[key]

    def __str__(self):
        string = "{} Elements in cache\n".format(len(self._cache))
        for key, descriptor in self._cache.items():
            string += "{}: {}\n".format(key, descriptor)
        string += "a"
        return string

cache = Cache()


class Attribute(object):
    def __init__(self, type, required, default=None, help=""):
        self.type = type
        self.default = default
        self.required = required
        self.help = help

    def __str__(self):
        return "{} {} {} {}".format(self.type, self.default, self.required, self.help)


class Descriptor(object):
    def __init__(self, name):
        self.name = name

    def parse(self, cfg):
        raise NotImplementedError("Please don't use basetype")


class IntDescriptor(Descriptor):
    @staticmethod
    def parse(value):
        if not isinstance(value, int):
            raise ValueError("Expected Int")
        return value


class BoolDescriptor(Descriptor):
    @staticmethod
    def parse(value):
        if not isinstance(value, bool):
            raise ValueError("Expected Boolean")
        return value


class FloatDescriptor(Descriptor):
    @staticmethod
    def parse(value):
        if not isinstance(value, float):
            raise ValueError("Expected Float")
        return value


class StringDescriptor(Descriptor):
    @staticmethod
    def parse(value):
        if not isinstance(value, str):
            raise ValueError("Expected String")
        return value


import json
class Config(dict):
    def __str__(self):
        return json.dumps(self, indent=4)

class CustomDescriptor(object):
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.cache = cache

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

    def parse_yaml(self, yaml_file):
        cfg = DescriptorFactory.read_from_yaml(yaml_file)
        return self.parse(cfg)

    def parse(self, cfg):
        import collections
        assert isinstance(cfg, collections.Mapping)

        is_valid = True
        parsed_config = Config()
        for key, attribute in self.attributes.items():
            if key not in cfg:
                if attribute.required:
                    raise ValueError("Missing value %s in config", key)
                logger.warning("Setting default value for %s", key)
            value = cfg.pop(key, attribute.default)
            descriptor = cache[attribute.type]
            try:
                value = descriptor.parse(value)
            except ValueError as e:
                print(key, value)
                raise
            parsed_config[key] = value
        if len(cfg) != 0:
            logger.warning("There are unused keys in this config: %s", " ,".join(cfg.keys()))
                
        return parsed_config

    def __len__(self):
        return len(self.attributes)


class DiscoveryService(object):
    """Also Update config during run time"""
    """That would actually be amazing"""
    """But would rebuild some objects as well"""


class AttributeFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def build(cfg):
        type = cfg.pop('type')
        required = cfg.pop('required')
        default = cfg.pop('default', None)
        help = cfg.pop('help', None)
        if len(cfg) != 0:
            raise ValueError("The config still contains values", cfg)
        return Attribute(type, required, default, help)


class DescriptorFactory(object):
    def __init__(self, *search_directory):
        """
        Args:
            search_directory: Directories that are searched for template files.
        """
        #add basetypes
        self.cache = cache
        self.cache['int'] = IntDescriptor
        self.cache['string'] = StringDescriptor
        self.cache['float'] = FloatDescriptor
        self.cache['bool'] = BoolDescriptor

        for path, name in discover(search_directory[0]):
            logger.debug("Found %s in %s", name, path)
            descriptor = self.build_simple_descriptor(path, name)
            self.cache[name] = descriptor

    @staticmethod
    def read_from_yaml(path):
        import yaml
        with open(path, 'r') as f:
            return yaml.load(f, yaml.SafeLoader)

    def build_simple_descriptor(self, path, name):
        if path.endswith('.yaml'):
            cfg = self.read_from_yaml(path)

        descriptor = CustomDescriptor(name)
        for key, values in cfg.items():
            attribute = AttributeFactory.build(values)
            descriptor.add_attribute(key, attribute)

        return descriptor

    def get_descriptor(self, identifier):
        return self.cache[identifier]

    def __str__(self):
        return str(self.cache)
