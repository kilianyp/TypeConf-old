from type_factory import TypeFactory

fac = TypeFactory()
fac.register_search_directory("descriptors")
node = fac.build_type("class1")
print(node.name)

