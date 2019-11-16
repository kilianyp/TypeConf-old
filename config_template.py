import os
import logging
import json

logger = logging.getLogger()



MAGIC_DEFAULT_VALUE = "SC_MAGIC_DEFAULT_VALUE"
class Attribute(object):
    def __init__(self, name, descriptor, required, default=MAGIC_DEFAULT_VALUE, help=""):
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
            # TODO default must be set WHAT if it wasnt set
            if self.default == MAGIC_DEFAULT_VALUE:
                raise ValueError("Value was not set but also no default value for {}".format(self.name))
            self.descriptor.value = self.default
            logger.warning("Setting default value for %s to %s", self.name, self.default)
        return self.descriptor.parse()

    def __str__(self):
        return "{} {} {} {} {}".format(self.name, self.default, self.required, self.help, self.descriptor.value)


class EvalType(Descriptor):
    def parse(self):
        if not isinstance(self.value, str):
            raise ValueError("Expected String")
        self.value = eval(self.value)
        return True
# class list
# class listoftype
# class of nestedtype
# class of regex


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
        for key, attribute in self.attributes.items():
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


class Config(dict):
    """ TODO access per dot.
        print with help"""
    def __str__(self):
        return json.dumps(self, indent=4)


class DiscoveryService(object):
    """Also Update config during run time"""
    """That would actually be amazing"""
    """But would rebuild some objects as well"""


# each type can only have a certain set of dependcies
# but each type can be the dependency of multiple types
# but what if we do not yet know the depndencies of the dependencies
# we cannot yet make a conclusion about cycles

# read class if we do not know the type yet continue until we know the type, if we finish error

class TypeTree(object):
    def __init__(self):
        self.types = {}

    def add_type(self, node):
        if node.name in self.types:
            raise ValueError("Type with name {} already exists.".format(node.name))
        self.types[node.name] = node


class TypeNode(object):
    def __init__(self, name):
        self.name = name
        # what if this type is not built yet
        self.childs = [] # types this type depends on
        self.cfg = None
        self.parents = [] # types that depend on this


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
        self.cache['eval'] = EvalType('eval')

        for path, name in discover(search_directory[0]):
            print("Found %s in %s" % (name, path))
            if os.path.isdir(path):
                type = self.build_folder_type(name)
            else:
                if path.endswith('.yaml'):
                    cfg = read_from_yaml(path)
                else:
                    raise FileNotFoundError(path)

                if cfg is None:
                    logger.warning("Skipping %s (%s)", name, path)
                    continue
                type = self.build_composite_type(cfg, name)
            self.cache[name] = type

    # TODO this is still mixed up
    # we have attributes, and multiple descriptor types
    def build_composite_type(self, cfg, name):
        type = CompositeType(name)
        for key, values in cfg.items():
            attribute = self.build_attribute(key, values)
            type.add_attribute(key, attribute)
        return type

    def build_folder_type(self, name):
        return OneOfType(name, self.cache[name])

    def __str__(self):
        return str(self.cache)

    def build_attribute(self, key, cfg):
        """ Returns Attribute"""
        import copy
        type = cfg.pop('type').lower()

        if type == "oneof":
            descriptor = OneOf(key)
            descriptor.add_options(cfg.pop('options'))
        elif type == "datatype":
            # TODO nice might be to have really a  dynamic class created and instantiate it
            descriptor = copy.deepcopy(self.cache[cfg.pop('dtype')])
        elif type == "const":
            descriptor = Const(key, cfg.pop('value'))
        else:
            # TODO differentiate between errors in templates and config
            raise ValueError("Error in Template {}: unknown type {}".format(key, type))

        required = cfg.pop('required')
        # TODO requires cfg.pop('requires')
        default = cfg.pop('default', None)
        help = cfg.pop('help', None)
        if len(cfg) != 0:
            raise ValueError(
                    "The config for {} contains unrecognized settings: {}"
                    .format(key, cfg))
        return Attribute(key, descriptor, required, default, help)


def dot2dict(dotstring, value):
    levels = dotstring.split('.')
    base_dic = {}
    last_dic = base_dic
    for l in levels[:-1]:
        last_dic[l] = {}
        last_dic = last_dic[l]
    last_dic[levels[-1]] = value
    return base_dic


class ConfigTemplate(object):
    def __init__(self, cache, name):
        self.name = name
        self.descriptor = cache[name]

    def fill_from_yaml(self, yaml_file):
        cfg = read_from_yaml(yaml_file)
        return self.fill_from_cfg(cfg)

    # TODO Think about grid search
    def fill_from_cl(self, unknown_args):
        for arg in unknown_args:
            path, sep, value = arg.partition("=")
            # could be split
            if sep == '=':
                nested = dot2dict(path, value)
                print(nested)
                self.descriptor.value = nested
            else:
                raise ValueError

        return 

    def fill_from_cfg(self, cfg):
        self.descriptor.value = cfg

    def to_config(self):
        self.descriptor.parse()
        return self.descriptor.to_config()
