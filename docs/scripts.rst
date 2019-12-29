Scripts
=======

Archiving
---------

archive_documents_simple.sh
```````````````````````````

Purpose
~~~~~~~

I use this script to archive important documents on USB
flash drives just in case all the backups fail or files
are deleted by mistake.

Steps
~~~~~

1. partition and format a USB drive
2. get the filesystem UUID with `lsblk -o name,uuid`
3. edit the configuration file

References
~~~~~~~~~~

- https://wiki.archlinux.org/index.php?title=Udisks&oldid=575618#udevadm_monitor

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Running user
~~~~~~~~~~~~

``root``

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+----------------------------------------------------+
| Name                 | Binaries   | Version          | Homepage                                           |
+======================+============+==================+====================================================+
| GNU Bash             | - bash     | 5.0.7(1)         | http://www.gnu.org/software/bash/bash.html         |
+----------------------+------------+------------------+----------------------------------------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

I use one configuration file per user.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one configuration file per user.

Licenses
~~~~~~~~

- GFDLv1.3+

YAML data
`````````

::

    <--YAML-->
    entry:
        name: archive_documents_simple.sh
        type: archiving
        configuration files:
            paths:
                - archive_documents_simple.myuser.conf
        systemd unit files:
            paths:
                service:
                    - archive-documents-simple.myuser.service
    <!--YAML-->
