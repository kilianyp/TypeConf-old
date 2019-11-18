from type_factory import FileTree

tree = FileTree()
tree.add(['a', 'b', 'c', 'd'])
tree.add(['a', 'b', 'c', 'e'])
tree.add(['a', 'b', 'f'])

print(tree.get(['a', 'b']))
print(tree.get(['a', 'b', 'c']))
