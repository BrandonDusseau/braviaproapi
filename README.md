# braviaproapi

**WARNING:** This library is in active development and is not ready for use. It is not yet available
on PyPI and its name and functionality are likely to change without notice.

Library for communicating with Sony Bravia TVs utilizing its Bravia Professional API.

## Requirements

This library requires Python 3.7 (tentative) or higher. You can install it with `pip install braviaproapi`.

## Enabling the API on the TV

These instructions are based on a 2015 Bravia TV running Android 7.0 (Nougat). The steps may differ on
newer devices.

**NOTE:** You should NEVER expose your television's API to the Internet directly as this poses a
significant security risk to your network and television. If you insist on controlling your TV
from outside your home network you should set up separate, more secure, software that only exposes
the functionality you need.

1. Open **Settings**
2. Select **Network > Home network > IP control**
3. Set **Authentication** to **Normal and Pre-Shared Key**
4. Select **Pre-Shared Key** and specify the passcode to initiate your API.

## Using the library

TO DO

## License

This project is released under the MIT License. Refer to the LICENSE file for details.
