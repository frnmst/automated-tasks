Coding standards
================

Python
------

- scripts must be written in Python >= 3.5 and Python < 4.
- scripts must start with ``#!/usr/bin/env python3``
- access to the shell is done via the fpyutils module when possible
- code must be validated through `$ make pep`
- Whenever possible use YAML for configuration files

Shell
-----

- scripts must be GNU Bash compatible.
- scripts must start with ``#!/usr/bin/env bash``
- scripts must set these options: ``set -euo pipefail``
- all variables must be enclosed in braces
- all variables must be quoted, except integers

