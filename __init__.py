from type_factory import TypeFactory
import inspect

fc = TypeFactory()

def get_factory():
    return fc


def config(name):
    def _config(func):
        executed = False
        def check_execution_fn(*args, **kwargs):
            # only add those values to config that were executed
            executed = True
            return func(*args, **kwargs)
        fc.register_function(name, func)
        return check_execution_fn

