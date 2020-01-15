Helper scripts
==============

Helper script are handle the way the main scripts are copied in your installation.
They are located under the ``./utils`` sirectory.

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
               ``deploy.py`` as root.

Steps
~~~~~

1. if needed, edit the ``SRC_DIR`` variable in the script.

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

This script copies all the scripts and their systemd unit files, as well as deploy.py
to the appropriate places ``./deploy.py``


----

prepare_environment.py
``````````````````````

generates the ``prepare_environment.sh`` script and the ``metadata.yaml`` file

