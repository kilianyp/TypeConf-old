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


class AttributeFactory(object):
    @staticmethod
    def build(name, descriptor, cfg):
        """ Returns Attribute"""
        required = cfg.pop('required')
        # TODO requires cfg.pop('requires')
        default = cfg.pop('default', None)
        help = cfg.pop('help', None)
        if len(cfg) != 0:
            raise ValueError(
                    "The config for {} contains unrecognized settings: {}"
                    .format(name, cfg))
        return Attribute(name, descriptor, required, default, help)
