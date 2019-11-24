from parser import IntType
import pytest

def test_int_parser():
    parser = IntType("test")
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
