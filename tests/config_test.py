from typeconf import TypeFactory

def test_to_config():
    fac = TypeFactory("tests/templates")
    config_template = fac.build_template('class1')
    config_template.fill_from_file("tests/configs/config.yaml")
    args = config_template.parse_args(['AttributeClass.Attribute1=5'])
    # set values manually
    config = config_template.to_config()
    assert config.AttributeClass.Attribute1 == 5
