class FileTree(object):
    """
    A simple to keep track of the subclasses of a folder
    """
    def __init__(self):
        self.nested = {}

    def add(self, name, structure):
        """This does not work
        if a directory is added before the file.
        Adds a file strucuture[-1] with name to the tree
        """
        level = self.nested
        for s in structure[:-1]:
            if s not in level:
                level[s] = {}
            level = level[s]
        level[structure[-1]] = name

    def get(self, structure):
        """
        Args:
            structure: The single parts of the path

        Returns:
            All files 
        """
        level = self.nested
        for s in structure:
            if s not in level:
                raise ValueError(f"File {s} does not exists in {level}")
            level = level[s]
        # TODO does not support nested folders
        all_files = []
        for val in level.values():
            if isinstance(val, dict):
                continue
            all_files.append(val)
        return all_files


