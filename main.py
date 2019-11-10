from config_template import ConfigTemplate, AttributeFactory, Cache
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('task')
args, unknown_args = parser.parse_known_args()


cache = Cache()
factory = AttributeFactory(cache, 'descriptors')
config_template = ConfigTemplate(cache, 'class1')

print(config_template.descriptor)
config_template.fill_from_yaml("config.yaml")
print(config_template.descriptor)
config_template.fill_from_cl(unknown_args)
# set values manually
config = config_template.to_config()
print(config)
