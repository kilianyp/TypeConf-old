from config_template import OneOf
import pytest
def test_one_of():
    descriptor = OneOf("test")
    descriptor.add_option("a")
    descriptor.add_options(["b", 2])

    descriptor.value = "b"

    descriptor.parse()

    descriptor.value = 1

    with pytest.raises(ValueError):
        descriptor.parse()


