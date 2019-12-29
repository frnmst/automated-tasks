Rules
=====

General
-------

- scripts are divided by topic and placed in different directories
  accordingly.
- if files are imported into a script, these will be classified as
  configuration files.
- scripts cannot run without configuration files.
- scripts or systemd unit files are optional: a standalone systemd unit file does the job in some cases.
  In this case configuration files are not needed. Conversely, a script does not need
  a systemd unit file if it is called directly by an external program.

Running users
-------------

===================   =============================================================================
User name             Description
===================   =============================================================================
``motion``            the user running the [motion](https://motion-project.github.io/index.html) instance
``mydesktopuser``     a generic user with Xorg access
``myuser``            a generic user with our without Xorg access
``root``              the root user
``surveillance``      a user running audio and/or video surveillance scripts or programs
``yacy``              the user running the [yacy](https://www.yacy.net/) instance
===================   =============================================================================

Coding standards
----------------

Shell scripts
`````````````

- scripts must be bash compatible.
- scripts must start with ``#!/usr/bin/env bash``
- scripts must set these options: ``set -euo pipefail``
- all variables must be enclosed in braces
- all variables must be quoted, except integers

Python scripts
``````````````

- scripts must be written in Python 3.
- scripts must start with ``#!/usr/bin/env python3``
- access to the shell must be done with ``subprocess.run``
- all shell variables must be quoted with ``shlex.quote``
- shell commands must be split with ``shlex.split``
