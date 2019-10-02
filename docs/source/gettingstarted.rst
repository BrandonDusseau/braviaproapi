Getting Started
===============

Configuring Your Television
###########################

.. danger::
  You should **NEVER** expose your television's API to the Internet directly as this poses a significant security
  risk to your network and television. If you insist on controlling your TV from outside your home network you should
  set up separate, more secure, software that only exposes the functionality you need.

These instructions are based on a 2015 Bravia TV running Android 7.0 (Nougat). The steps may differ on newer devices.

To make your television's API accessible to this library:

  1. Open Settings
  2. Select Network > Home network > IP control
  3. Set Authentication to Normal and Pre-Shared Key
  4. Select Pre-Shared Key and specify your passcode of choice.
  5. Make note of your television's IP address. You may want to make it static to avoid connection loss.

That's it! Now you can begin controlling your television.


Installing The Library
######################

This library is published to PyPI and can be easily installed by running the below command (preferably in a
`virtualenv <https://pipenv.kennethreitz.org/en/latest/>`_). Python 3.7 or higher is required to use this library.

.. code-block:: console

  pip install braviaproapi

Sending Commands
################

.. tip::
  Full documentation of available commands and the BraviaClient is available on the `braviaproapi <braviaproapi.html>`_
  page.

Now that you have the library available, let's set up the client, change the volume, change inputs, and open an app.

.. code-block:: python

  from braviaproapi import BraviaClient

  television = BraviaClient(host="192.168.1.200", passcode="0000")

  # Wake up the TV if it's asleep
  is_powered_on = television.system.get_power_status()
  if not is_powered_on:
      television.system.power_on()

  # Change input to HDMI 2
  television.avcontent.set_play_content("extInput:hdmi?port=2")

  # Set the volume to 20%
  television.audio.set_volume_level(20)

  # Play roulette? Open the first app the TV returns.
  apps = television.appcontrol.get_application_list(exclude_builtin=True)
  television.appcontrol.set_active_app(apps[0].get("uri"))


Feel like going retro? You can send raw remote control commands as well. A list of remote codes is available at
`braviaproapi.bravia.remote <braviaproapi.bravia.remote.html>`_.

.. code-block:: python

  from braviaproapi import BraviaClient
  from braviaproapi.bravia import ButtonCode

  television = BraviaClient(host="192.168.1.200", passcode="0000")

  television.remote.send_button(ButtonCode.POWER)
  television.remote.send_button(ButtonCode.HDMI_1)


Handling Errors
###############

Since Sony's API documentation is a little sketchy, you should be prepared to handle errors raised by the library.
See `braviaproapi.bravia.errors <braviaproapi.bravia.errors.html>`_ for a list of possible errors that may arise
due to user error, problems with the library, or device-specific issues. The function documentation also
indicates which errors may be raised by each function.
