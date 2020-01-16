Rules
=====

Summary
-------

- all the scripts, this documentation and their dependencies are `free software <https://www.gnu.org/philosophy/free-sw.html>`_.
- scripts are divided by categories and placed in different directories
  accordingly. See the ``./src`` directory
- if files are imported into a script, these will be classified as
  configuration files
- scripts cannot run without configuration files
- scripts or systemd unit files are optional:

  - standalone systemd unit file does the job in some cases. In this case configuration files are not needed
  - a script does not need a systemd unit file if it is called directly by an external program

Running
-------

Go into the ``./utils`` directory and run these steps:

1. generate the ``metadata.yaml`` file
2. generate a shell script, called  ``prepare_environment.sh``, based on the content of the ``metadata.yaml`` file.
3. run the ``prepare_environment.sh`` script as root.


::


    $ ./prepare_environment.py prepare_environment.conf --generate-yaml > metadata.yaml
    $ ./prepare_environment.py prepare_environment.conf > prepare_environment.sh
    $ chmod +x ./prepare_environment.sh
    # ./prepare_environment.sh


Script users
------------

===================   ======================================================================================
User name             Description
===================   ======================================================================================
``motion``            the user running the `Motion <https://motion-project.github.io/index.html>`_ instance
``mydesktopuser``     a generic user with Xorg access
``myuser``            a generic user with our without Xorg access
``root``              the root user
``surveillance``      a user running audio and/or video surveillance scripts or programs
``yacy``              the user running the `YaCy <https://www.yacy.net/>`_ instance
===================   ======================================================================================

The metadata.yaml file
----------------------

The ``./metadata.yaml`` file contains important information for the deployment of the scripts.
This file is generated automatically using some of the data present in this documentation.

Important YAML keys
```````````````````

- the ``*`` character matches any value.

=================================================  ========  ================================================
YAML Key                                           Optional  Optional only if condition
=================================================  ========  ================================================
``[*][*][configuration files]``                    yes       no script is present (see the "General" section)     
``[*][*][systemd unit files][paths][service]``     no
``[*][*][systemd unit files][paths][timer]``       yes
=================================================  ========  ================================================

Coding standards
----------------

Shell scripts
`````````````

- scripts must be GNU Bash compatible.
- scripts must start with ``#!/usr/bin/env bash``
- scripts must set these options: ``set -euo pipefail``
- all variables must be enclosed in braces
- all variables must be quoted, except integers

Python scripts
``````````````

- scripts must be written in Python >= 3.5 and Python < 4.
- scripts must start with ``#!/usr/bin/env python3``
- access to the shell must be done with ``subprocess.run``
- all shell variables must be quoted with ``shlex.quote``
- shell commands must be split with ``shlex.split``
