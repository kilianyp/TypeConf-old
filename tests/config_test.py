from argparse import ArgumentParser
from type_factory import TypeFactory
from config_template import ConfigTemplate

fac = TypeFactory()
fac.register_search_directory("tests/descriptors")
descriptor = fac.get('class1')

parser = ArgumentParser()
parser.add_argument('task')
args, unknown_args = parser.parse_known_args()

config_template = ConfigTemplate(descriptor, 'class1')

print(config_template.descriptor)
config_template.fill_from_file("tests/configs/config.yaml")
print(config_template.descriptor)
config_template.fill_from_cl(unknown_args)
# set values manually
config = config_template.to_config()
print(config)
