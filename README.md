# TypeConf

## A static configuration parser for python using templates

Python is as a dynamic programming language inherently prone to runtime errors. This  is especially problematic for long-running programms. A wrong or missing value in the configuration then can lead very easily to the loss of your precious computation.

Sounds familiar?

TypeConf builds a configuration parser from templates, that can be hierarchical nested to define your individual configuration. This template can be easily parsed then at the beginning of your code and checked for your individual requirements.

Furthermore, TypeConf helps maintain up-to-date configurations by quickly revealing broken configurations and making easy to support old configurations despite changes.

# Installation

## From PyPi

```
pip install typeconf
```

## From source

```
pip install git+https://github.com/kilsenp/TypeConf.git
```

# Demo

```yaml
# templates/parent.yaml
attr_int:
    dtype: int
    required: False
    help: "This is an int"
    default: 0
    type: "datatype"
attr_child:
    dtype: child
    required: False
    help: "This a type constructed from another yaml"
    type: "datatype"
```

```yaml
# templates/child.yaml
attr_bool:
    dtype: bool
    required: True
    help: "This is a bool"
    type: "datatype"
```

TypeConf will be automatically be able to solve the dependencies when building the type.

```python
# main.py
from typeconf import TypeFactory
factory = TypeFactory()
factory.register_search_directory('templates')
template = factory.build_template('parent')
```

We can now pass a config file to be parsed.

```yaml
# config.yaml
attr_child:
    attr_bool: True
```

```python
template.fill_from_file('config.yaml')
```

This values can also be overwritten by command line arguments, addressing subconfigs through dot separated names.

```python
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('task')
# python main.py test attr_child.attr_bool=False
args, unknown_args = parser.parse_known_args()
# args.task = test
template.fill_from_cl(unknown_args)
```

Finally we create the config that can be used throughout the rest of the code.

```python
config = template.to_config()  # Actual parsing happens here
# {
#    attr_int: 0,
#    attr_child: {
#       attr_bool: False  #overwritten by cli
#    }
# }
```

# Features

- Static configuration parsing before program is started
- Easy verification of existing configurations, if they still work with the current pipeline
- Easy extension of existing configurations by adding default values to templates
- Automatically make types within a subfolder choosable
- Comment individual configuration values
- Overwrite values using the command line or from code
- Data type testing, ensure the correct datatype:
  - int
  - float
  - str
  - bool

## TODO

- [x] clean split between types, attributes, special types
- [ ] Consistent naming
- [ ] Allow more combinations e.g. choice of + datatype
- [ ] better error messages
- [ ] config from python file
- [ ] unit tests
- [ ] @config_file('path_to_cfg')
- [ ] eval and type are not exclusive. make additional attribute
- [ ] Pretty print with comments
- [x] Command line interface
- [ ] Conditional requirements. If a is set b also has to be set. Better if b is a part of a? Leads to duplicates
- [ ] Generation of a seed.
- [x] Pip Package
- [ ] Github Services
- [ ] Copy From to ensure same training as validation, or make it as default?
- [ ] ensure two values are equal, but then why even set two?
- [ ] Config updates, pass multiple configs
