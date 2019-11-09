import os
import logging
import json

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


class Attribute(object):
    def __init__(self, name, descriptor, required, default=None, help=""):
        self.name = name
        self.descriptor = descriptor
        self.required = required
        # TODO requires
        self.default = default
        self.help = help

    def parse(self):
        if not self.descriptor.isset:
            if self.required:
                raise ValueError("Value not set %s", self.name, self.descriptor)
            logger.warning("Setting default value for %s", self.name)
            # TODO default must be set WHAT if it wasnt set
            self.descriptor.value = self.default
        return self.descriptor.parse()

    def __str__(self):
        return "{} {} {} {} {}".format(self.name, self.default, self.required, self.help, self.descriptor.value)


class Descriptor(object):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.isset = True

    def __init__(self, name):
        self.name = name
        self._value = None
        self.isset = False

    def parse(self):
        raise NotImplementedError()

    def to_config(self):
        return self.value


class IntType(Descriptor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse(self):
        if not isinstance(self.value, int):
            raise ValueError("Expected Int")
        return True


class BoolType(Descriptor):
    def parse(self):
        if not isinstance(self.value, bool):
            raise ValueError("Expected Boolean")
        return True


class FloatAttribute(Descriptor):
    def parse(self):
        if not isinstance(self.value, float):
            raise ValueError("Expected Float")
        return True


class StringAttribute(Descriptor):
    def parse(self):
        if not isinstance(self.value, str):
            raise ValueError("Expected String")
        return True


class OneOf(Descriptor):
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
        for key, attribute in self.attributes.items():
            if key not in value:
                continue
            attribute.descriptor.value = value.pop(key)

        if len(value) != 0:
            logger.warning("There are unused keys in this config: %s", " ,".join(value.keys()))

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


def read_from_yaml(path):
    import yaml
    with open(path, 'r') as f:
        return yaml.load(f, yaml.SafeLoader)


class Config(dict):
    """ TODO access per dot.
        print with help"""
    def __str__(self):
        return json.dumps(self, indent=4)


class DiscoveryService(object):
    """Also Update config during run time"""
    """That would actually be amazing"""
    """But would rebuild some objects as well"""


class AttributeFactory(object):
    def __init__(self, cache, *search_directory):
        """
        Args:
            search_directory: Directories that are searched for template files.
        """
        #add basetypes
        self.cache = cache
        self.cache['int'] = IntType('int')
        self.cache['string'] = StringAttribute('string')
        self.cache['float'] = FloatAttribute('float')
        self.cache['bool'] = BoolType('bool')

        for path, name in discover(search_directory[0]):
            logger.debug("Found %s in %s", name, path)
            type = self.build_composite_type(path, name)
            self.cache[name] = type

    # TODO this is still mixed up
    def build_composite_type(self, path, name):
        if path.endswith('.yaml'):
            cfg = read_from_yaml(path)

        type = CompositeType(name)

        for key, values in cfg.items():
            attribute = self.build_simple_attribute(key, values)
            type.add_attribute(key, attribute)
        return type

    def build_simple_attribute(self, key, cfg):
        """ Returns Attribute"""
        import copy
        if "options" in cfg:
            type = OneOf(key)
            type.add_options(cfg.pop('options'))
        else:
            type = cfg.pop('type')
            type = copy.deepcopy(self.cache[type])

        required = cfg.pop('required')
        # TODO requires cfg.pop('requires')
        default = cfg.pop('default', None)
        help = cfg.pop('help', None)
        if len(cfg) != 0:
            raise ValueError("The config still contains values", cfg)
        return Attribute(key, type, required, default, help)

    def __str__(self):
        return str(self.cache)



class ConfigTemplate(object):
    def __init__(self, cache, name):
        self.name = name
        self.descriptor = cache[name]

    def fill_from_yaml(self, yaml_file):
        cfg = read_from_yaml(yaml_file)
        return self.fill_from_cfg(cfg)

    def fill_from_cfg(self, cfg):
        self.descriptor.value = cfg

    def to_config(self):
        self.descriptor.parse()
        return self.descriptor.to_config()
