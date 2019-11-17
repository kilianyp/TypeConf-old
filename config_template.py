import logging
import utils as u

logger = logging.getLogger()

class ConfigTemplate(object):
    def __init__(self, descriptor, name):
        self.name = name
        self.descriptor = descriptor

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
                self.descriptor.value = nested
            else:
                raise ValueError
        return

    def fill_from_cfg(self, cfg):
        self.descriptor.value = cfg

    def to_config(self):
        self.descriptor.parse()
        return self.descriptor.to_config()
