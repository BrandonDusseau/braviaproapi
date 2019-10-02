# braviaproapi

[![Documentation Status](https://readthedocs.org/projects/braviaproapi/badge/?version=latest)](https://braviaproapi.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/BrandonDusseau/braviaproapi.svg?branch=master)](https://travis-ci.org/BrandonDusseau/braviaproapi)

This library provides an easy-to-use Python interface for controlling Sony Bravia televisions. It implements the
BRAVIA Professional Display API, which is present on recent consumer hardware. For more information, take a look at
[Sony's API documentation](https://pro-bravia.sony.net/develop/integrate/ip-control/).

It supports the following features:

  * Control and launch applications, including text entry into form fields.
  * Configuration of display and audio options
  * Control over various system functions (sleep/wake, LED configuration, power saving, etc.)
  * Direct control of external inputs and media sources
  * Emulated remote control input via IRCC commands

This library is intended for use on newer, Android-based televisions, and has been tested on 2015 and 2016 Bravia
models running Android 7.0 (Nougat).

## Requirements

This library supports Python 3.7 and higher. You can install it with `pip install braviaproapi`.


## Documentation / Getting Started

You can view the documentation for this project at [Read The Docs](https://braviaproapi.readthedocs.io/).


## Generating Documentation Locally

Generating the documentation for this project requires
[Sphinx](http://www.sphinx-doc.org/en/master/usage/installation.html). Installing from pip is recommended.

Once Sphinx is installed, run these commands to generate documentation (requires GNU make):

```bash
cd docs
make html
```


## Contributing

See an issue? Have something to add? Issues and pull requests are accepted in this repository.


## License

This project is released under the MIT License. Refer to the LICENSE file for details.
