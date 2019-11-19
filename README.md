# A typesafe, hierachical config for python using templates
This is not the first python config library that claims to be typesafe
[1](https://github.com/beetbox/confuse),
[2](https://github.com/chimpler/pyhocon).
These libraries require to specify the type during runtime.
In some circumstances, however, it is better to be able to guarantee a correct configuration 
before the actual routine starts.
This allows to avoid costly mistakes where the model cannot be safed because of the wrong type.

So why not just code a check in the beginning?
Creating templates allows to store all default values and 
their corresponding types neatly for easy checking.
Furthermore, the templates are reusable.

# Features
- FileType:
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
- [x] clean split between types, attributes, special types
- [ ] better error messages
- [ ] config from python file
- [ ] unit tests
- [ ] @config_file('path_to_cfg')
- [ ] eval and type are not exclusive. make additional attribute
- [ ] Better name parser instead of type?
- [ ] Pretty print with comments
- [x] Command line interface
- [ ] Conditional requirements. If a is set b also has to be set. Better if b is a part of a? Leads to duplicates
- [ ] Generation of a seed.
- [ ] Pip Package
- [ ] Github Services
