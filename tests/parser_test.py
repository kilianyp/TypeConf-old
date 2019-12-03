from typeconf import parser as p
import pytest

def test_int_parser():
    parser = p.IntType("test")
    parser.value = 1
    parser.parse()
    parser.value = "1"
    parser.parse()
    with pytest.raises(ValueError):
        parser.value = 1.0
        parser.parse()
    with pytest.raises(ValueError):
        parser.value = True
        parser.parse()
    with pytest.raises(ValueError):
        parser.value = 1.1
        parser.parse()
    with pytest.raises(ValueError):
        parser.value = "1.1"
        parser.parse()
