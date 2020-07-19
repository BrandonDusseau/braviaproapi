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

## Compatibility

This library is intended for use on newer, Android-based televisions. A list of devices and software versions known to be compatible is available on [the GitHub wiki](https://github.com/BrandonDusseau/braviaproapi/wiki/Compatible-Device-List).

It has come to my attention that some newer Bravia models have received software updates bumping their API version to higher than 3.x. These devices are not supported by braviaproapi at this time as I do not have a compatible device to test with. Contributions to the library (and the above linked wiki page) are encouraged if you have a supported device!

If your device is not compatible, braviaproapi will raise the following exception on first connection:

    braviaproapi.bravia.errors.apierror.ApiError: The target device is running an incompatible API version 'X.Y.Z'

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
