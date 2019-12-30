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
2. get the filesystem UUID with ``$ lsblk -o name,uuid``
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
~~~~~~~~~


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


----

extract_gpx_data_from_dashcams.sh
`````````````````````````````````

Purpose
~~~~~~~

I use this script to delete old dashcam footage and replace it with
gpx data extracted from the footage itself. This works
for my *AUKEY DR02 D* dashcam (with its separate GPS unit).
It should work for other dashcams as well.

You can open the generated gpx files with programs like
`GPXSee <https://www.gpxsee.org/>`_
or `GPX-viewer <https://blog.sarine.nl/tag/gpxviewer/>`_.

Steps
~~~~~

1. put the dashcam footage in the appropriate directory
2. edit the configuration file
3. edit the `gpx.fmt` file if needed

.. important:: do not skip step 3. Read the comments in the file.

References
~~~~~~~~~~

- https://www.topografix.com/gpx_manual.asp
- http://owl.phy.queensu.ca/~phil/exiftool/geotag.html#Inverse
- https://sno.phy.queensu.ca/~phil/exiftool/TagNames/GPS.html
- https://sno.phy.queensu.ca/~phil/exiftool/faq.html

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash
- perl

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+----------------------------------------------------+
| Name                 | Binaries   | Version          | Homepage                                           |
+======================+============+==================+====================================================+
| GNU Bash             | - bash     | 5.0.7(1)         | http://www.gnu.org/software/bash/bash.html         |
+----------------------+------------+------------------+----------------------------------------------------+
| GNU Coreutils        | - printf   | 8.31             | https://www.gnu.org/software/coreutils/            |
|                      | - sync     |                  |                                                    |
|                      | - sort     |                  |                                                    |
|                      | - sha1sum  |                  |                                                    |
|                      | - rm       |                  |                                                    |
+----------------------+------------+------------------+----------------------------------------------------+
| Findutils            | - find     | 4.6.0            | https://www.gnu.org/software/findutils/            |
|                      | - xargs    |                  |                                                    |
+----------------------+------------+------------------+----------------------------------------------------+
| Gawk                 | - gawk     | 4.2.1            | http://www.gnu.org/software/gawk/                  |
+----------------------+------------+------------------+----------------------------------------------------+
| exiftool             | - exiftool | 11.50            | http://search.cpan.org/perldoc?exiftool            |
+----------------------+------------+------------------+----------------------------------------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

I use one configuration file per dashcam.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one configuration file per dashcam.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start extract-gpx-data-from-dashcams.myuser.timer``

Enable
......

``# systemctl enable extract-gpx-data-from-dashcams.myuser.timer``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    extract_gpx_data_from_dashcams.sh:
        type: archiving
        running user: myuser
        configuration files:
            paths:
                - gpx.fmt
                - extract_gpx_data_from_dashcams.myuser.conf
        systemd unit files:
            paths:
                service:
                    - extract-gpx-data-from-dashcams.myuser.service
                timer:
                    - extract-gpx-data-from-dashcams.myuser.timer
    <!--YAML-->
