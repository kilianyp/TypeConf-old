import os
SUPPORTED_FILETYPES = ['.yaml', '.json']
MAGIC_SPLIT_NAME = '.'
DEFAULT_DESCRIPTOR_PATH = 'protos'
IGNORE_FOLDERS = ["__pycache__", './']

FILE_ENUM = 1
DIR_ENUM = 2


def discover(basepath=DEFAULT_DESCRIPTOR_PATH, prefix=''):
    """
    Recursively check for supported files
    we need to first build the ones without dependencies, which are in the subfolders,
    descriptors on the same level cannot depend on each other
    we do this by seeing the folder structure hierachically
    TODO
    first subfolders before files
    files in subfolders before subfolder
    """
    for f in os.listdir(basepath):
        if f in IGNORE_FOLDERS:
            continue

        path = os.path.join(basepath, f)

        if os.path.isdir(path):
            for returnvalue in discover(path, prefix + f + MAGIC_SPLIT_NAME):
                yield returnvalue
            yield path, prefix + f, DIR_ENUM
        elif os.path.isfile(path):
            for ftype in SUPPORTED_FILETYPES:
                if f.endswith(ftype):
                    yield path, prefix + f.rstrip(ftype), FILE_ENUM
                    break
        else:
            raise RuntimeError("Not supported case TODO")


def read_file(path):
    if path.endswith('.yaml'):
        return read_from_yaml(path)

    raise ValueError(f"Unknown File Ending {path}")


def read_from_yaml(path):
    import yaml
    with open(path, 'r') as f:
        return yaml.load(f, yaml.SafeLoader)
