# A typesafe, hierarchical configuration for python using templates
The idea of this project is that you can define a configuration that is parsed before the actual
program is run.
Therefore, no unwanted surprises during the run of the program should happen.
This is in contrast to other typesafe libraries
([1](https://github.com/beetbox/confuse),
[2](https://github.com/chimpler/pyhocon))
that check the type when it is fetched from the configuration.

This is designed in particular for setups that require longer calculations before saving
the current progress (for example ML).

Furthermore, it tries to help maintain up-to-date configurations that still work despite
new configuration options.

# Demo
tests/config_test.py

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
- [ ] Copy From to ensure same training as validation, or make it as default?
- [ ] ensure two values are equal, but then why even set two?
- [ ] Config updates, pass multiple configs
