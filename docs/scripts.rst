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

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| GNU Bash             | - bash     | 5.0.7(1)         |
+----------------------+------------+------------------+
| GNU Coreutils        | - env      | 8.31             |
|                      | - stdbuf   |                  |
|                      | - sync     |                  |
+----------------------+------------+------------------+
| util-linux           | - mount    | 2.34             |
|                      | - umount   |                  |
+----------------------+------------+------------------+
| rsync                | - rsync    | 3.1.3            |
+----------------------+------------+------------------+
| systemd              | - udevadm  | 242.29           |
+----------------------+------------+------------------+

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

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| GNU Bash             | - bash     | 5.0.7(1)         |
+----------------------+------------+------------------+
| GNU Coreutils        | - env      | 8.31             |
|                      | - sync     |                  |
|                      | - sort     |                  |
|                      | - sha1sum  |                  |
|                      | - rm       |                  |
+----------------------+------------+------------------+
| Findutils            | - find     | 4.6.0            |
|                      | - xargs    |                  |
+----------------------+------------+------------------+
| Gawk                 | - gawk     | 4.2.1            |
+----------------------+------------+------------------+
| exiftool             | - exiftool | 11.50            |
+----------------------+------------+------------------+

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

pdftoocr.sh
```````````

Purpose
~~~~~~~

I use this script to transform paper documents in ocr'd PDFs.

This script processes one file per directory.

The output filename will be the SHA 1 sum of the directory name.

For example, given:

``documents/a/out.pdf``

three files will result:

- ``documents/a/86f7e437faa5a7fce15d1ddcb9eaeaea377667b8.pdf``: the compressed, archivable, grayscaled and OCR'd version of ``out.pdf``
- ``documents/a/86f7e437faa5a7fce15d1ddcb9eaeaea377667b8.pdf.txt``: a txt file of the OCR'd text from ``out.pdf``
- ``documents/a/SHA512SUMS``: a checksum file containing the SHA 512 checksums of ``documents/a/86f7e437faa5a7fce15d1ddcb9eaeaea377667b8.pdf`` and ``documents/a/86f7e437faa5a7fce15d1ddcb9eaeaea377667b8.pdf.txt``

Infact:


::


    $ echo -n 'a' | sha1sum


is ``86f7e437faa5a7fce15d1ddcb9eaeaea377667b8``.

Steps
~~~~~

1. install the appropriate tesseract language data files
2. install the `JBIG2 Encoder <https://github.com/agl/jbig2enc>`_
3. edit the configuration files
4. scan documents with ``$ simple-scan``
5. save the output file as ${OUTPUT_FILE}
6. if you want to keep colors, run ``$ touch "${COLOR_OVERRIDE_FILE}"`` in
   the directory. This file will be automatically deleted once the script ends.

References
~~~~~~~~~~

- https://unix.stackexchange.com/a/93971

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| GNU Bash             | - bash     | 5.0.7(1)         |
+----------------------+------------+------------------+
| Findutils            | - find     | 4.6.0            |
+----------------------+------------+------------------+
| Gawk                 | - gawk     | 4.2.1            |
+----------------------+------------+------------------+
| GNU Coreutils        | - chmod    | 8.31             |
|                      | - cp       |                  |
|                      | - date     |                  |
|                      | - env      |                  |
|                      | - rm       |                  |
|                      | - sha1sum  |                  |
|                      | - sha512sum|                  |
|                      | - sort     |                  |
|                      | - sync     |                  |
|                      | - tr       |                  |
+----------------------+------------+------------------+
| Ghostscript          | - gs       | 9.27             |
+----------------------+------------+------------------+
| OCRmyPDF             | - ocrmypdf | 8.3.0            |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

.. important:: It is very important to set the OCR_LANG variable.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one unit file per document root.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start pdftoocr.myuser-documents.timer``

Enable
......

``# systemctl enable pdftoocr.myuser-documents.timer``

Licenses
~~~~~~~~

- CC-BY-SA 3.0

YAML data
~~~~~~~~~


::


    <--YAML-->
    pdftoocr.sh:
        type: archiving
        running user: myuser
        configuration files:
            paths:
                - pdftoocr_deploy.sh
                - pdftoocr_deploy.myuser_documents.conf
                - pdftoocr.myuser_documents.conf
        systemd unit files:
            paths:
                service:
                    - pdftoocr.myuser-documents.service
                timer:
                    - pdftoocr.myuser-documents.timer
    <!--YAML-->


----

youtube_dl.sh
`````````````

Purpose
~~~~~~~

I use this script to download and archive videos from various platforms.

Steps
~~~~~

1. get a list of urls and divide them by subject
2. edit the configuration files
3. optionally install `Gotify <https://github.com/gotify/server>`_ and run an instance

References
~~~~~~~~~~

- https://wiki.archlinux.org/index.php/Youtube-dl
- https://gotify.net/
- https://gotify.net/docs/pushmsg

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Dependencies
~~~~~~~~~~~~

+----------------------+----------------+------------------+
| Name                 | Binaries       | Version          |
+======================+================+==================+
| GNU Bash             | - bash         | 5.0.11(1)        |
+----------------------+----------------+------------------+
| GNU Coreutils        | - env          | 8.31             |
|                      | - mkdir        |                  |
|                      | - wc           |                  |
+----------------------+----------------+------------------+
| Findutils            | - find         | 4.7.0            |
+----------------------+----------------+------------------+
| youtube-dl           | - youtube-dl   | 2019.10.22       |
+----------------------+----------------+------------------+
| FFmpeg               |                | 1:4.2.1          |
+----------------------+----------------+------------------+
| aria2                |                | 1.34.0           |
+----------------------+----------------+------------------+
| Gawk                 | - gawk         | 5.0.1            |
+----------------------+----------------+------------------+
| curl                 | - curl         | 7.66.0           |
+----------------------+----------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Three files must exist for each subject:

1. the ``*.conf`` file is a generic configuration file
2. the ``*.options`` file contains most of the options used by ``youtube-dl``
3. the ``*txt`` file contains a list of source URLs

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one configuration file per subject.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start youtube-dl.some-subject.timer``

Enable
......

``# systemctl enable youtube-dl.some-subject.timer``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    youtube_dl.sh:
        type: archiving
        running user: myuser
        configuration files:
            paths:
                - youtube_dl.some_subject.conf
                - youtube_dl.some_subject.options
                - youtube_dl.some_subject.txt
        systemd unit files:
            paths:
                service:
                    - youtube-dl.some-subject.service
                timer:
                    - youtube-dl.some-subject.timer
    <!--YAML-->


----

archive_invoice_files.py
````````````````````````

Purpose
~~~~~~~

I use this script to archive and print invoice files.

Invoice files are downloaded from PEC accounts (certified mail) as attachments.
An HTML file corresponding to the XML invoice file is archived and
printed. Finally, a notification is sent to a Gotify instance.
During this process, cryptographical signatures and integrity checks are performed.

Steps
~~~~~

1. Create a new virtual environment as explained in 
   `this post <https://gitlab.com/frnmst/frnmst.gitlab.io/blob/master/_posts/2019-11-10-running-python-scripts-with-different-package-versions.md>`_,
   and call it ``archive_invoice_files``
2. within the virtual environment Install the listed python dependencies with ``pip3``.
3. edit the configuration file
4. optionally install `Gotify <https://github.com/gotify/server>`_ and run an instance

References
~~~~~~~~~~

- https://github.com/markuz/scripts/blob/master/getmail.py

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
| Requests                   |            | 2.22.0           |
+----------------------------+------------+------------------+
| dateutil                   |            | 2.8.1            |
+----------------------------+------------+------------------+
| lxml                       |            | 4.4.1            |
+----------------------------+------------+------------------+
| pycups                     |            | 1.9.74           |
+----------------------------+------------+------------------+
| WeasyPrint                 |            | 50               |
+----------------------------+------------+------------------+
| fattura-elettronica-reader |            | 0.1.0            |
+----------------------------+------------+------------------+

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

``#  systemctl start archive-invoice-files.myuser.timer``

Enable
......

``# systemctl enable systemctl start archive-invoice-files.myuser.timer``

Licenses
~~~~~~~~

- GPLv2+
- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    archive_invoice_files.py:
        type: archiving
        running user: myuser
        configuration files:
            paths:
                - archive_invoice_files.myuser.conf
        systemd unit files:
            paths:
                service:
                    - archive-invoice-files.myuser.service
                timer:
                    - archive-invoice-files.myuser.timer
    <!--YAML-->


----


archive_media_files.sh
``````````````````````

Purpose
~~~~~~~

I use this script to archive media files, specifically photos and
videos, from removable drives such as SD cards.

Files are archived using this schema:


::


    ${device_uuid}/${year}/${month}


Udisks2 hanged frequently, so I had to write this new script which
uses traditional mount commands. Parallelization was also added.

Steps
~~~~~

1. get a device with media files
2. get the filesystem UUID with: ``$ lsblk -o name,uuid``
3. get the user id and group id of the user corresponding to the
   path where the files will be archived
4. edit the configuration file

References
~~~~~~~~~~

- https://wiki.archlinux.org/index.php?title=Udisks&oldid=575618#udevadm_monitor
- https://github.com/frnmst/automated-tasks/blob/67415cdd7224ff21a2f39bb8180ee36cf6e6e31e/archiving/archive_documents_simple.sh
- https://frnmst.gitlab.io/notes/automatic-removable-media-synchronization.html

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| GNU Bash             | - bash     | 5.0.11(1)        |
+----------------------+------------+------------------+
| GNU Coreutils        | - basename | 8.31             |
|                      | - cut      |                  |
|                      | - date     |                  |
|                      | - env      |                  |
|                      | - mkdir    |                  |
|                      | - rm       |                  |
|                      | - stat     |                  |
|                      | - stdbuf   |                  |
|                      | - sync     |                  |
|                      | - wc       |                  |
+----------------------+------------+------------------+
| util-linux           | - mount    | 2.34             |
|                      | - umount   |                  |
+----------------------+------------+------------------+
| rsync                | - rsync    | 3.1.3            |
+----------------------+------------+------------------+
| systemd              | - udevadm  | 243.78           |
+----------------------+------------+------------------+
| GNU Parallel         | - parallel | 20190722         |
+----------------------+------------+------------------+
| Findutils            | - find     | 4.7.0            |
+----------------------+------------+------------------+
| exiftool             | - exiftool | 11.70            |
+----------------------+------------+------------------+
| GNU C Library        | - getent   | 2.30             |
+----------------------+------------+------------------+
| curl                 | - curl     | 7.67.0           |
+----------------------+------------+------------------+
| Gawk                 | - gawk     | 5.0.1            |
+----------------------+------------+------------------+
| sudo                 | - sudo     | 1.8.29           |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

I use one configuration file per purpose.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one configuration file per purpose.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start archive-media-files.mypurpose.service``

Enable
......

``# systemctl enable archive-media-files.mypurpose.service``

Licenses
~~~~~~~~

- GFDLv1.3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    archive_media_files.sh:
        type: archiving
        running user: root
        configuration files:
            paths:
                - archive_media_files.mypurpose.conf
        systemd unit files:
            paths:
                service:
                    - archive-media-files.mypurpose.service
    <!--YAML-->


----

Backups
-------

borgmatic_hooks.sh
``````````````````

Purpose
~~~~~~~

I use this script to send notifications during hard drive backups. A script to
mount the backed up archives is also included here.

Steps
~~~~~

1. create a new borg repository. Our backups will lie near the sources: we want
   to avoid encryption because it will work with older version of borg.
   For local repositories run:


   ::


       $ borg init -e none /full/path/to/the/repository.borg


   For remore repositories run:


   ::


       $ borg init -e none user@host:/full/path/to/the/repository.borg


2. edit the Borgmatic YAML configuration file
3. edit the configuration files

References
~~~~~~~~~~

- https://torsion.org/borgmatic/
- https://torsion.org/borgmatic/docs/how-to/monitor-your-backups/
- https://torsion.org/borgmatic/docs/how-to/deal-with-very-large-backups/
- https://borgbackup.readthedocs.io/en/stable/usage/init.html?highlight=encryption
- https://medspx.fr/projects/backup/
- https://borgbackup.readthedocs.io/en/stable/deployment/image-backup.html
- https://projects.torsion.org/witten/borgmatic/raw/branch/master/sample/systemd/borgmatic.service
- https://projects.torsion.org/witten/borgmatic/raw/branch/master/sample/systemd/borgmatic.timer

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| GNU Bash             | - bash     | 5.0.11(1)        |
+----------------------+------------+------------------+
| GNU Coreutils        | - env      | 8.31             |
|                      | - mkdir    |                  |
|                      | - tail     |                  |
+----------------------+------------+------------------+
| borgmatic            | - borgmatic| 1.4.21           |
+----------------------+------------+------------------+
| curl                 | - curl     | 7.67.0           |
+----------------------+------------+------------------+
| Python-LLFUSE        |            | 1.3.6            |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

I use a set of configuration files per mountpoint to back up.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use a set of configuration files per mountpoint to back up.

To mount all trhe archives of a borg backup you simply must run:


::


    # systemctl start borgmatic-mount.myhostname_backed_up_mountpoint.service


and to unmount them:


::


    # systemctl stop borgmatic-mount.myhostname_backed_up_mountpoint.service


Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start borgmatic.myhostname_backed_up_mountpoint.timer``

Enable
......

``# systemctl enable borgmatic.myhostname_backed_up_mountpoint.timer``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    borgmatic_hooks.sh:
        type: backups
        running user: root
        configuration files:
            paths:
                - borgmatic.myhostname_backed_up_mountpoint.yaml
                - borgmatic_hooks.myhostname_backed_up_mountpoint.conf
                - borgmatic_mount.myhostname_backed_up_mountpoint.conf
                - archive_documents_simple.myuser.conf
        systemd unit files:
            paths:
                service:
                    - borgmatic.myhostname_backed_up_mountpoint.service
                    - borgmatic-mount.myhostname_backed_up_mountpoint.service
                timer:
                    - borgmatic.myhostname_backed_up_mountpoint.timer
    <!--YAML-->


----

Drives
------

smartd_test.py
``````````````

Purpose
~~~~~~~

I use this to run periodical S.M.A.R.T. tests on the hard drives.

Steps
~~~~~

1. run ``# hdparm -I ${drive}`` and compare the results with
   ``$ ls /dev/disk/by-id`` to know which drive corresponds to the
   one you want to work on
2. edit the configuration file
3. optionally install `Gotify <https://github.com/gotify/server>`_ and run an instance

References
~~~~~~~~~~

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- python

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| Python               | - python3  | 3.7.4            |
+----------------------+------------+------------------+
| Smartmontools        | - smartctl | 7.0              |
+----------------------+------------+------------------+
| Requests             |            | 2.22.0           |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

The script supports only ``/dev/disk/by-id`` names.

See also the udev rule file ``/lib/udev/rules.d/60-persistent-storage.rules``.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one file per drive so I can control when a certain drive
performs testing, instead of running them all at once.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start smartd-test.ata-disk1.timer``

Enable
......

``# systemctl enable smartd-test.ata-disk1.timer``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    smartd_test.py:
        type: drives
        running user: root
        configuration files:
            paths:
                - smartd_test.conf
        systemd unit files:
            paths:
                service:
                    - smartd-test.ata-disk1.service
                timer:
                    - smartd-test.ata-disk1.timer
    <!--YAML-->


