from argparse import ArgumentParser
from typeconf import TypeFactory

def test_to_config():
    fac = TypeFactory()
    fac.register_search_directory("tests/templates")

    parser = ArgumentParser()
    parser.add_argument('task')
    args, unknown_args = parser.parse_known_args(['test', 'AttributeClass.Attribute1=5'])

    config_template = fac.build_template('class1')
    config_template.fill_from_file("tests/configs/config.yaml")
    config_template.fill_from_cl(unknown_args)
    # set values manually
    config = config_template.to_config()
    assert config.AttributeClass.Attribute1 == 5
