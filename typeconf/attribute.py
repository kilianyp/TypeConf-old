import logging

logger = logging.getLogger()

MAGIC_DEFAULT_VALUE = "SC_MAGIC_DEFAULT_VALUE"


class Attribute(object):
    def __init__(
            self,
            name,
            parser,
            required,
            default=MAGIC_DEFAULT_VALUE,
            evaluate=False,
            const=False,
            help=""):
        self.name = name
        self.parser = parser
        self.required = required
        # TODO requires
        self.default = default
        self.help = help
        self.eval = evaluate
        self.const = const

    def parse(self):
        if not self.parser.isset:
            if self.required:
                raise ValueError("Value not set %s", self.name, self.parser)
            # TODO default must be set WHAT if it wasnt set
            if self.default == MAGIC_DEFAULT_VALUE:
                raise ValueError("Value was not set but also no default value for {}".format(self.name))
            self.parser.value = self.default
            logger.warning("Setting default value for %s to %s", self.name, self.default)
        else:
            # value was set
            if self.const:
                # alternatively create a type
                # allows to check if the value was changed
                raise ValueError("{} is const, cannot set value {}".format(self.name, self.parser.value))

        if self.eval:
            self.parser.value = eval(self.parser.value)
        return self.parser()

    def __str__(self):
        return "{} {} {} {} {}".format(self.name, self.default, self.required, self.help, self.parser.value)


class AttributeFactory(object):
    @staticmethod
    def build(name, parser, cfg):
        """ Returns Attribute"""
        required = cfg.pop('required')
        # TODO requires cfg.pop('requires')
        default = cfg.pop('default', None)
        help = cfg.pop('help', None)
        eval = cfg.pop('eval', False)
        const = cfg.pop('const', False)
        if len(cfg) != 0:
            raise ValueError(
                    "The config for {} contains unrecognized settings: {}"
                    .format(name, cfg))
        return Attribute(name, parser, required, default,eval, const, help)
