from config_template import DescriptorFactory

factory = DescriptorFactory('descriptors')
experiment_descriptor = factory.get_descriptor('class1')
# argparser = experiment_descriptor.get_argparser()
# print(experiment_descriptor)
config = experiment_descriptor.parse_yaml("config.yaml")
print(config)
