from config_template import ConfigTemplate, AttributeFactory

factory = AttributeFactory('descriptors')
config_template = ConfigTemplate('class1')

# argparser = experiment_descriptor.get_argparser()
print(config_template.descriptor)
config_template.fill_from_yaml("config.yaml")
print(config_template.descriptor)
# experiment_descriptor.fill_from_cl()
# set values manually
config = config_template.to_config()
print(config)
