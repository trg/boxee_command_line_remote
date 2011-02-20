boxee.py
========

What it is
----------
Command line Boxee remote.

Tested with Boxee Box & Python 2.6 on Mac OS X

Installation
------------

Copy boxee.py to your local PATH (often /usr/local/bin )

Example (OS X, Linux):

$ sudo cp boxee.py /usr/local/bin/boxee

$ sudo chmod +x /usr/local/bin/boxee

No configuration is required, as boxee.py will find the boxee app
on your network.

Usage
-----

From the terminal, interactive mode:

$ boxee

To send a command directly:

$ boxee vol 50


Known issues
------------

May have unexpected results if more than one Boxee Box or app is on your network.

Occasionally network-related hanging.

Has crashed my Boxee Box a few times.