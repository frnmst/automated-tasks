Coding standards
================

Python
------

- scripts must be written in Python >= 3.5 and Python < 4.
- scripts must start with ``#!/usr/bin/env python3``
- access to the shell must be done with ``subprocess.run``
- all shell variables must be quoted with ``shlex.quote``
- shell commands must be split with ``shlex.split``

Shell
-----

- scripts must be GNU Bash compatible.
- scripts must start with ``#!/usr/bin/env bash``
- scripts must set these options: ``set -euo pipefail``
- all variables must be enclosed in braces
- all variables must be quoted, except integers

