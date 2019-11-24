from type_factory import FileTree
import pytest

def test_file_tree():
    tree = FileTree()
    tree.add("node1", ['a', 'b', 'c', 'd.file'])
    tree.add("node2", ['a', 'b', 'c', 'e.file'])
    tree.add("node3", ['a', 'b', 'f'])
    print(tree.get(['a', 'b']))
    assert list(tree.get(['a', 'b', 'c'])) == ['node1', 'node2']
    with pytest.raises(ValueError):
        tree.get(['g'])
