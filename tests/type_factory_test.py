from type_factory import TypeFactory

fac = TypeFactory()
fac.register_search_directory("descriptors")
descriptor = fac.get('class1')
print(descriptor)
print(descriptor)

