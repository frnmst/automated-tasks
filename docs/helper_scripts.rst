Helper scripts
==============

Helper scripts handle the way the main scripts are installed.
They are located under the ``./utils`` directory.

Installable
-----------

deploy.py
`````````

Purpose
~~~~~~~

This script copies the systemd unit files from the services-by-user
directory to the appropriate systemd directory. It also start and enables the
newly copied systemd units. If a timer unit is not available, the service
unit is enabled and started instead.

.. important:: Every time you change a service or timer file you must run
               ``deploy.py`` as root to update the installed unit files.

Steps
~~~~~

1. if needed, edit the ``SRC_DIR`` variable in the script

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- python

Dependencies
~~~~~~~~~~~~

+----------------------------+------------+------------------+
| Name                       | Binaries   | Version          |
+============================+============+==================+
| Python                     | - python3  | 3.7.4            |
+----------------------------+------------+------------------+

Licenses
~~~~~~~~

- GPLv3+

----

Non-installable
---------------

prepare_environment.sh
``````````````````````

Purpose
~~~~~~~

This script copies all the scripts and their systemd unit files, as well as ``deploy.py``
to the appropriate places 

.. note:: This file is generated dynamically by ``prepare_environment.py``.

Steps
~~~~~

1. if needed, edit the ``SRC_DIR`` variable in the script

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Dependencies
~~~~~~~~~~~~

+---------------------+------------+------------------+
| Name                | Binaries   | Version          |
+=====================+============+==================+
| GNU Coreutils       | - mkdir    | 8.31             |
|                     | - cp       |                  |
|                     | - chown    |                  |
|                     | - chmod    |                  |
+---------------------+------------+------------------+
| shadow              | - useradd  | 4.7              |
|                     | - usermod  |                  |
+---------------------+------------+------------------+

Licenses
~~~~~~~~

- GPLv3+

----

prepare_environment.py
``````````````````````

Purpose
~~~~~~~

Generates the ``prepare_environment.sh`` script and the ``metadata.yaml`` file

Steps
~~~~~

1. if necessary edit the ``prepare_environment.conf`` configuration file

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- python

Dependencies
~~~~~~~~~~~~

+---------------------+------------+------------------+
| Name                | Binaries   | Version          |
+=====================+============+==================+
| Python              | - python3  | 3.7.4            |
+---------------------+------------+------------------+

Licenses
~~~~~~~~

- GPLv3+
