class Parser(object):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.isset = True

    def __init__(self, name):
        self.name = name
        self._value = None
        self.isset = False

    def __call__(self):
        return self.parse()

    def parse(self):
        raise NotImplementedError()

    def to_config(self):
        return self.value


class IntType(Parser):
    def parse(self):
        if isinstance(self.value, int):
            return True
        # TODO better check for string
        if isinstance(self.value, str) and self.value.isdigit():
            self.value = int(self.value)
            return True
        raise ValueError("Expected Int")


class FloatType(Parser):
    @staticmethod
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def parse(self):
        if isinstance(self.value, float):
            return True
        if isinstance(self.value, str) and self.isfloat(self.value):
            self.value = float(self.value)
            return True
        raise ValueError("Expected Float")


class BoolType(Parser):
    def parse(self):
        if isinstance(self.value, bool):
            return True
        if self.value.lower() == "false":
            self.value = False
            return True
        if self.value.lower() == "true":
            self.value = True
            return True

        raise ValueError("Expected Boolean")


class StringType(Parser):
    def parse(self):
        if not isinstance(self.value, str):
            raise ValueError("Expected String")
        return True


class EvalType(Parser):
    def parse(self):
        if not isinstance(self.value, str):
            raise ValueError("Expected String")
        self.value = eval(self.value)
        return True


BASE_TYPES = {
    'int': IntType,
    'float': FloatType,
    'bool': BoolType,
    'string': StringType,
    'eval': EvalType
}


# class list
# class listoftype
# class of nestedtype
# class of regex
