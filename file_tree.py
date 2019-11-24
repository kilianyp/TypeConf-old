class FileTree(object):
    """
    A simple to keep track of the subclasses of a folder
    """
    def __init__(self):
        self.nested = {}

    def add(self, name, structure):
        """This does not work
        if a directory is added before the file.
        """
        level = self.nested
        for s in structure[:-1]:
            if s not in level:
                level[s] = {}
            level = level[s]
        level[structure[-1]] = name

    def get(self, structure):
        level = self.nested
        for s in structure:
            if s not in level:
                raise ValueError(f"File {s} does not exists in {level}")
            level = level[s]
        return level.values()


