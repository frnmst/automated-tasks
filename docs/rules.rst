Rules
=====

Basics
------

- all the scripts, this documentation and their dependencies are `free software <https://www.gnu.org/philosophy/free-sw.html>`_.

Structure
`````````

- scripts and systemd unit files are divided by categories and placed in different directories
  accordingly. See the ``./src`` directory
- if files are imported into a script, these will be classified as
  configuration files
- scripts cannot run without configuration files
- scripts or systemd unit files are optional:

  - standalone systemd unit file does the job in some cases. In this case configuration files are not needed
  - a script does not need a systemd unit file if it is called directly by an external program

Dependencies
~~~~~~~~~~~~

Scripts page 
............

- dependencies are referred to the machine where the services need to be installed
- the versions reported here are valid at the moment of writing

References page
...............

- the list of software is as generic as possible

File naming
-----------

Configuration and systemd unit files follow naming schemes that make easier to relate multiple services to configurations and multiple
configurations to scripts.

Variables
`````````

================            =====================              =====================
Variable                    Configuration                      Systemd unit file 
================            =====================              =====================
``script_name``             ``_`` separated words              ``-`` separated words
``subject``                 ``_`` separated words              ``_`` separated words
================            =====================              =====================

Rules
`````

- optional variables and constants are reported between square brackets (``[`` and ``]``)

============================    ====================================================    =================================================
Script                          Configuration                                           Systemd unit file
============================    ====================================================    =================================================
``${script_name}.{py,sh}``      ``${script_name}.[${subject}.]{conf,options}``          ``${script_name}.[${subject}.]{service,timer}``
============================    ====================================================    =================================================

The metadata.yaml file
----------------------

The ``./utils/metadata.yaml`` file contains important information for the deployment of the scripts.

.. important:: Since `commit 8852e61 <https://github.com/frnmst/automated-tasks/commit/8852e6109bbf6bfffcadaf2727e62f6f4eed3e67>`_ this file is generated automatically using some of the data present in this documentation.

Coding standards
----------------

Shell
`````

- scripts must be GNU Bash compatible.
- scripts must start with ``#!/usr/bin/env bash``
- scripts must set these options: ``set -euo pipefail``
- all variables must be enclosed in braces
- all variables must be quoted, except integers

Python
``````

- scripts must be written in Python >= 3.5 and Python < 4.
- scripts must start with ``#!/usr/bin/env python3``
- access to the shell must be done with ``subprocess.run``
- all shell variables must be quoted with ``shlex.quote``
- shell commands must be split with ``shlex.split``

Scripts page schema
-------------------

Rules
`````

- optional elements must be omitted if empty

Schema
``````

The following schema represents a single entry.


.. code-block:: html
    :linenos:


    <h3>${script name}</h3>             # required
    <h4>Purpose</h4>                    # required
    <p></p>                             # required
    <h4>Steps</h4>                      # an implicit step for all scripts is to edit the configuration file{,s}
    <ol>                                
        <li></li>                       # 1->n
    </ol>
    <h4>References</h4>
    <ul>
        <li></li>                       # 1->n
    </ul>
    <h4>Programming languages</h4>      # required
    <ul>                                # required
        <li></li>                       # required, 1->n
    </ul>
    <h4>Dependencies</h4>               # required
    <table>
        <tr>                            # required
            <th>Name</th>
            <th>Binaries</th>
            <th>Version</th>
        </tr>
        <tr>                            # required
            <td></td>                   # requited
            <td>
                <ul>
                    <li></li>           # 0->n
                </ul>
            </td>
            <td></td>                   # required
        </tr>
    </table>
    </table>
    <h4>Configuration files</h4>
    <p></p>
    <h4>Systemd unit files</h4>
    <p></p>
    <h4>Licenses</h4>                   # required
    <ul>                                # required
        <li></li>                       # required, 1->n
    </ul>
    <h4>YAML data/h4>                   # required
    <pre></pre>                         # required
    <hr />                              # required
