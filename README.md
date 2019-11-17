# A typesafe config for python
# Motivation:
Why not just check and set it in Code:
- harder to read
- spread across files
- where are defaults set
- What was wrong with sacred:
-- All values were in config
# TODO:
- Pretty print with comments
- @config_file('path_to_cfg')


Raise Errors during config parsing:
- Config contains a value that is not specified in the proto (To avoid passing wrong and using default values instead)
- Value is of wrong type
- Value is constant

Raises error:
- When config file is overwritten after parsing. Config should be fixed.

Supports:
- default data types:
    - int
    - float
    - str
- custom data types: Which can be built from default data types
- Default values
- Required
- Comment



## TODO
- [x] Command line interface
- [ ] Conditional requirements. If a is set b also has to be set. Better if b is a part of a? Leads to duplicates
- [ ] Generation of a seed.

