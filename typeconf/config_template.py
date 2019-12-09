import logging
from . import utils as u
from argparse import ArgumentParser

logger = logging.getLogger()

class ConfigTemplate(object):
    def __init__(self, name, parser):
        self.name = name
        self.parser = parser
        self.argument_parser = ArgumentParser()

    def parse_args(self, args=None):
        args, unknown_args = self.argument_parser.parse_known_args(args)
        self.fill_from_cl(unknown_args)
        return args

    def fill_from_file(self, path):
        cfg = u.read_file(path)
        return self.fill_from_cfg(cfg)

    # TODO Think about grid search
    def fill_from_cl(self, unknown_args):
        for arg in unknown_args:
            path, sep, value = arg.partition("=")
            # could be split
            if sep == '=':
                nested = u.dot2dict(path, value)
                self.parser.value = nested
            else:
                raise ValueError
        return

    def fill_from_cfg(self, cfg):
        self.parser.value = cfg

    def to_config(self):
        self.parser.parse()
        return self.parser.to_config()



