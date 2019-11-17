import os
SUPPORTED_FILETYPES = ['.yaml', '.json']
DEFAULT_DESCRIPTOR_PATH = 'protos'
IGNORE_FOLDERS = ["__pycache__", './']

FILE_ENUM = 1
DIR_ENUM = 2


def dot2dict(dotstring, value):
    levels = dotstring.split('.')
    base_dic = {}
    last_dic = base_dic
    for l in levels[:-1]:
        last_dic[l] = {}
        last_dic = last_dic[l]
    last_dic[levels[-1]] = value
    return base_dic


def discover(basepath=DEFAULT_DESCRIPTOR_PATH, structure=[]):
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
            # return subfiles before parent folder!
            sub_structure = structure.copy()
            sub_structure.append(f)
            for returnvalue in discover(path, sub_structure):
                yield returnvalue
            yield path, sub_structure, DIR_ENUM
        elif os.path.isfile(path):
            for ftype in SUPPORTED_FILETYPES:
                if f.endswith(ftype):
                    sub_structure = structure.copy()
                    sub_structure.append(f.rstrip(ftype))
                    yield path, sub_structure, FILE_ENUM
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
