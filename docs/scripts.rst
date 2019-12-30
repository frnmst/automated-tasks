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

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+----------------------------------------------------+
| Name                 | Binaries   | Version          | Homepage                                           |
+======================+============+==================+====================================================+
| GNU Bash             | - bash     | 5.0.7(1)         | http://www.gnu.org/software/bash/bash.html         |
+----------------------+------------+------------------+----------------------------------------------------+
| GNU Coreutils        | - stdbuf   | 8.31             | https://www.gnu.org/software/coreutils/            |
|                      | - sync     |                  |                                                    |
+----------------------+------------+------------------+----------------------------------------------------+
| util-linux           | - mount    | 2.34             | https://github.com/karelzak/util-linux             |
|                      | - umount   |                  |                                                    |
+----------------------+------------+------------------+----------------------------------------------------+
| rsync                | - rsync    | 3.1.3            | https://rsync.samba.org/                           |
+----------------------+------------+------------------+----------------------------------------------------+
| systemd              | - udevadm  | 242.29           | https://www.github.com/systemd/systemd             |
+----------------------+------------+------------------+----------------------------------------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

I use one configuration file per user.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one configuration file per user.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start archive-documents-simple.myuser.service``

Enable
......

``# systemctl enable archive-documents-simple.myuser.service``

Licenses
~~~~~~~~

- GFDLv1.3+

YAML data
`````````

::

    <--YAML-->
    archive_documents_simple.sh:
        type: archiving
        running user: root
        configuration files:
            paths:
                - archive_documents_simple.myuser.conf
        systemd unit files:
            paths:
                service:
                    - archive-documents-simple.myuser.service
    <!--YAML-->
