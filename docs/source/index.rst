braviaproapi - Sony Bravia API Client
=====================================

This library provides an easy-to-use Python interface for controlling Sony Bravia televisions. It implements the
BRAVIA Professional Display API, which is present on recent consumer hardware. For more information, take a look at
`Sony's API documentation <https://pro-bravia.sony.net/develop/integrate/ip-control/>`_.

It supports the following features:

    * Control and launch applications, including text entry into form fields.
    * Configuration of display and audio options
    * Control over various system functions (sleep/wake, LED configuration, power saving, etc.)
    * Direct control of external inputs and media sources
    * Emulated remote control input via IRCC commands

Take a look at the `Getting Started <gettingstarted.html>`_ page to learn how to use the library.

Compatibility
#############

This library is intended for use on newer, Android-based televisions. A list of devices and software versions known to
be compatible is available on
`the GitHub wiki <https://github.com/BrandonDusseau/braviaproapi/wiki/Compatible-Device-List>`_.

It has come to my attention that some newer Bravia models have received software updates bumping their API version to
higher than 3.x. These devices are not supported by braviaproapi at this time as I do not have a compatible device to
test with. Contributions to the library (and the above linked wiki page) are encouraged if you have a supported device!

Contributing
############

See something that could be improved? Pull requests and issues are accepted at the project's
`GitHub repository <https://www.github.com/BrandonDusseau/braviaproapi>`_.


Table of Contents
#################

.. toctree::
    :maxdepth: 2

    gettingstarted
    braviaproapi
