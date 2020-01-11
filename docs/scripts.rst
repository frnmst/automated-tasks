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
        category: archiving
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
        category: archiving
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
        category: archiving
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
        category: archiving
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
        category: archiving
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
        category: archiving
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

   We will assume that:

   - our source directory is a mountpoint at ``/backed/up/mountpoint``. This makes sense if we want to backup ``/root`` or ``/home`` for example.
   - we want to back up to a different partition's filesystem mounted at: ``/mnt/backups/myhostname_backed_up_mountpoint``

   To create a local repository run:


   ::


       $ borg init -e none /mnt/backups/myhostname_backed_up_mountpoint/myhostname_backed_up_mountpoint.borg


   For remore repositories run:


   ::


       $ borg init -e none user@host:/mnt/backups/myhostname_backed_up_mountpoint/myhostname_backed_up_mountpoint.borg


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

To mount all the archives of a borg backup you simply must run:


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
        category: backups
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
        category: drives
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

mdamd_check.py
``````````````

Purpose
~~~~~~~

I use this to run periodical RAID data scrubs on the hard drives.

Steps
~~~~~

1. run ``$ lsblk`` to know the names of the mdadm devices. See also: ``$ cat /proc/mdstat``
2. edit the configuration file
3. optionally install `Gotify <https://github.com/gotify/server>`_ and run an instance

References
~~~~~~~~~~

- https://frnmst.gitlab.io/notes/raid-data-scrubbing.html

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- python

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| Python               | - python3  | 3.7.3            |
+----------------------+------------+------------------+
| Requests             |            | 2.22.0           |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start mdamd-check.timer``

Enable
......

``# systemctl enable mdamd-check.timer``

Licenses
~~~~~~~~

- GPLv2+

YAML data
~~~~~~~~~


::


    <--YAML-->
    mdamd_check.py:
        category: drives
        running user: root
        configuration files:
            paths:
                - mdadm_check.conf
        systemd unit files:
            paths:
                service:
                    - mdamd-check.service
                timer:
                    - mdamd-check.timer
    <!--YAML-->


----

xfs_defrag.py
`````````````

Purpose
~~~~~~~

I use this script to run periodic defragmentations on XFS filesystems.

Steps
~~~~~

1. run ``$ lsblk -o name,uuid`` and get the UUID of the partition you want to defragment
2. edit the configuration file
3. optionally install `Gotify <https://github.com/gotify/server>`_ and run an instance

References
~~~~~~~~~~

- https://brashear.me/blog/2017/07/30/adventures-in-xfs-defragmentation/

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- python

Dependencies
~~~~~~~~~~~~

+----------------------+------------+------------------+
| Name                 | Binaries   | Version          |
+======================+============+==================+
| Python               | - python3  | 3.8.0            |
+----------------------+------------+------------------+
| util-linux           | - lsblk    | 2.34             |
+----------------------+------------+------------------+
| Requests             |            | 2.22.0           |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

This script supports only ``/dev/disk/by-uuid`` names.

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start xfs-defrag.my-uuid.timer``

Enable
......

``# systemctl enable xfs-defrag.my-uuid.timer``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    mdamd_check.py:
        category: drives
        running user: root
        configuration files:
            paths:
                - xfs_defrag.conf
        systemd unit files:
            paths:
                service:
                    - xfs-defrag.my-uuid.service
                timer:
                    - xfs-defrag.my-uuid.timer
    <!--YAML-->


----

Desktop
-------

random_wallpaper.sh
```````````````````

Purpose
~~~~~~~

I use this to automatically change wallpaper every few minutes.

Steps
~~~~~

1. edit the configuration file with image URLs or paths

References
~~~~~~~~~~

- https://linuxdifficile.wordpress.com/2014/04/24/sfondo-desktop-dinamico-per-linux/

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
| GNU Coreutils        | - shuf     | 8.31             |
+----------------------+------------+------------------+
| feh                  | - feh      | 3.2              |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Only 1 URL or path is allowed per line. feh will raise an error 
if an empty line is parsed.

.. important:: The configuration file must contain only URLs or paths.

.. warning:: No filter is made for the configuration file. It is your responsability
             for its content.

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start random-wallpaper.timer``

Enable
......

``# systemctl enable random-wallpaper.timer``

Licenses
~~~~~~~~

- CC-BY-SA 2.5

YAML data
~~~~~~~~~


::


    <--YAML-->
    random_wallpaper.sh:
        category: desktop
        running user: mydesktopuser
        configuration files:
            paths:
                - random_wallpaper.conf
        systemd unit files:
            paths:
                service:
                    - random-wallpaper.service
                timer:
                    - random-wallpaper.timer
    <!--YAML-->


----

set_display_gamma.sh
````````````````````

Purpose
~~~~~~~

I use this to automatically set a better gamma for the output on a tv.

Steps
~~~~~

1. edit the configuration file

References
~~~~~~~~~~

- https://askubuntu.com/a/62270

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
| Xorg                 | - xrandr   | 1.5.0            |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Make sure that the ``XORG_DISPLAY`` variable is set correctly.

To find out the current display variable run ``$ echo ${DISPLAY}``

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start set-display-gamma.timer``

Enable
......

``# systemctl enable set-display-gamma.timer``

Licenses
~~~~~~~~

- CC-BY-SA 3.0

YAML data
~~~~~~~~~


::


    <--YAML-->
    set_display_gamma.sh:
        category: desktop
        running user: mydesktopuser
        configuration files:
            paths:
                - set_display_gamma.TV_HDMI1.conf
        systemd unit files:
            paths:
                service:
                    - set-display-gamma.service
                timer:
                    - set-display-gamma.timer
    <!--YAML-->


----

Misc
----

vdirsyncer
``````````

Purpose
~~~~~~~

I use this to automatically syncronize my calendars and contacts.

Steps
~~~~~

1. setup Vdirsyncer and you clients (in my case, `Khal <https://lostpackets.de/khal/>`_ and `Todoman <https://github.com/pimutils/todoman>`_)

References
~~~~~~~~~~

- http://vdirsyncer.pimutils.org/en/stable/tutorials/systemd-timer.html

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash

Dependencies
~~~~~~~~~~~~

+----------------------+----------------+------------------+
| Name                 | Binaries       | Version          |
+======================+================+==================+
| Vdirsyncer           | - vdirsyncer   | 0.16.7           |
+----------------------+----------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start vdirsyncer.timer``

Enable
......

``# systemctl enable vdirsyncer.timer``

Licenses
~~~~~~~~

- BSD

YAML data
~~~~~~~~~


::


    <--YAML-->
    vdirsyncer:
        category: misc
        running user: myuser
        systemd unit files:
            paths:
                service:
                    - vdirsyncer.service
                timer:
                    - vdirsyncer.timer
    <!--YAML-->


----

monitor_and_notify_git_repo_changes.sh
``````````````````````````````````````

Purpose
~~~~~~~

My `Gitea <https://gitea.io/en-us/>`_ instance is configured to mirror
some repositories. Every 30 minutes this script checks for new
commits in those bare git repositories. If something new
is commited a notification is sent to my `Gotify <https://github.com/gotify/server>`_ 
instance.

.. note:: This script also works for non-bare git repositories.

Steps
~~~~~

1. install `Gotify <https://github.com/gotify/server>`_ and run an instance
2. edit the configuration file

References
~~~~~~~~~~

- https://gitea.io/en-us/
- https://gotify.net/
- https://gotify.net/docs/pushmsg

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
| curl                 | - curl     | 7.66.0           |
+----------------------+------------+------------------+
| Git                  | - git      | 2.23.0           |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

To avoid missing or reading duplicate messages, the variable
``CHECK_TIMEOUT_INTERVAL_SECONDS`` should be set
to the same value as the one in the systemd timer unit
file (``OnCalendar``).

I use one configuration file per group of repositories.

Systemd unit files
~~~~~~~~~~~~~~~~~~

I use one configuration file per group of repositories.

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start monitor-and-notify-git-repo-changes.myrepos.timer``

Enable
......

``# systemctl enable monitor-and-notify-git-repo-changes.myrepos.timer``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    monitor_and_notify_git_repo_changes.sh:
        category: misc
        running user: gitea
        configuration files:
            paths:
                - monitor_and_notify_git_repo_changes.myrepos.conf
        systemd unit files:
            paths:
                service:
                    - monitor-and-notify-git-repo-changes.myrepos.service
                timer:
                    - monitor-and-notify-git-repo-changes.myrepos.timer
    <!--YAML-->


----

yacy
````

Purpose
~~~~~~~

A personal search engine.

Steps
~~~~~

1. setup `YaCy <https://yacy.net/index.html>`_ and run an instance
2. create a `yacy` user and group
3. clone the YaCy search server repository into ``/home/yacy``: 


  ::


      $ git clone https://github.com/yacy/yacy_search_serve.git


References
~~~~~~~~~~

- https://yacy.net/index.html
- https://github.com/yacy/yacy_search_server

Programming languages
~~~~~~~~~~~~~~~~~~~~~

- bash
- java

Dependencies
~~~~~~~~~~~~

+----------------------+----------------+------------------+
| Name                 | Binaries       | Version          |
+======================+================+==================+
| YaCy                 | - startYACY.sh |                  |
|                      | - stopYACY.sh  |                  |
+----------------------+----------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start yacy-search-server.service``

Enable
......

``# systemctl enable yacy-search-server.service``

Licenses
~~~~~~~~

- LGPLv2+

YAML data
~~~~~~~~~


::


    <--YAML-->
    yacy:
        category: misc
        running user: yacy
        systemd unit files:
            paths:
                service:
                    - yacy-search-server.service
    <!--YAML-->


----


notify_camera_action.sh
```````````````````````

Purpose
~~~~~~~

Notify when a camera connected to a system running `Motion <https://motion-project.github.io/>`_
is found or lost (disconnected).

.. important:: We wil assume that a `Motion <https://motion-project.github.io/>`
               instance is configured and running.

Steps
~~~~~

1. edit a camera's configuration file with:


  ::


      # Run camera actions.
      on_camera_lost /home/jobs/scripts/by-user/motion/notify_camera_action.sh /home/jobs/scripts/by-user/motion/notify_camera_action.conf "%$ (id: %t)" "lost"
      on_camera_found /home/jobs/scripts/by-user/motion/notify_camera_action.sh /home/jobs/scripts/by-user/motion/notify_camera_action.conf "%$ (id: %t)" "found"


2. optionally install `Gotify <https://github.com/gotify/server>`_ and run an instance

References
~~~~~~~~~~

- https://motion-project.github.io/motion_config.html

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
| GNU Coreutils        | - stdbuf   | 8.31             |
|                      | - sync     |                  |
+----------------------+------------+------------------+
| curl                 | - curl     | 7.67.0           |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

A single file is used for all the cameras connected to a system.

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

Enable
......

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    notify_camera_action.sh:
        category: misc
        running user: motion
        configuration files:
            paths:
                - notify_camera_action.conf
    <!--YAML-->


----

System
------

hblock_unbound.sh
`````````````````

Purpose
~~~~~~~

I use this script to block malicious domains at a DNS level for the whole
internal network.

.. important:: We will assume that `Unbound <https://nlnetlabs.nl/projects/unbound/about/>`_ is configured and running.

Steps
~~~~~

1. separate Unbound's configuration into a header and footer file. 
   Have a look at the provided configuration files.
2. Clone the hblock repository: ``$ git clone https://github.com/hectorm/hblock.git``

References
~~~~~~~~~~

- https://github.com/hectorm/hblock

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
| Unbound              | - unbound  | 1.9.2            |
+----------------------+------------+------------------+
| Git                  | - git      | 2.22.0           |
+----------------------+------------+------------------+
| hblock               | - hblock   | 2.0.11           |
+----------------------+------------+------------------+
| GNU Make             | - make     | 4.2.1            |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

This script supports only ``/dev/disk/by-uuid`` names.
In case something goes wrong you can use this fallback command:

::


    # cat hblock_unbound.header.conf hblock_unbound.footer.conf > /etc/unbound/unbound.conf


.. note:: The provided configuration files are designed to work 
          along with `dnscrypt-proxy 2 <https://github.com/jedisct1/dnscrypt-proxy>`_

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start hblock-unbound.timer``

Enable
......

``# systemctl enable hblock-unbound.timer``

Licenses
~~~~~~~~

- MIT

YAML data
~~~~~~~~~


::


    <--YAML-->
     hblock_unbound.sh:
        category: system
        running user: root
        configuration files:
            paths:
                - hblock_unbound.footer.conf
                - hblock_unbound.header.conf
                - hblock_unbound.post_commands.conf
        systemd unit files:
            paths:
                service:
                    - hblock-unbound.service
                timer:
                    - hblock-unbound.timer
    <!--YAML-->



clean_pacman.sh
```````````````

Purpose
~~~~~~~

I use this very simple script to clean the cache generated by `Pacman <https://www.archlinux.org/pacman/>`_.

Steps
~~~~~

References
~~~~~~~~~~

- https://wiki.archlinux.org/index.php/Pacman#Cleaning_the_package_cache
- https://wiki.archlinux.org/index.php/Pacman/Tips_and_tricks#Removing_unused_packages_.28orphans.29

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
| pacman-contrib       | - paccache | 1.2.0            |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start clean-pacman.timer``

Enable
......

``# systemctl enable clean-pacman.timer``

Licenses
~~~~~~~~

- GFDLv1.3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    clean_pacman.sh:
        category: system
        running user: root
        systemd unit files:
            paths:
                service:
                    - clean-pacman.service
                timer:
                    - clean-pacman.timer
    <!--YAML-->


----

Audio
------

set-turntable-loopback-sound.sh
```````````````````````````````

Purpose
~~~~~~~

I use this script to enable the loopback sound of a
SONY PS-LX300USB turntable.

Steps
~~~~~

1. connect the turntable via USB 2.0 type B to the computer

References
~~~~~~~~~~

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
| alsa-utils           | - arecord  | 1.1.9            |
|                      | - aplay    |                  |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

To avoid ``aplay`` bloking the output, configure ALSA with
dmix PCMs. Use `aplay -l` to find the device names.

In my case I also want to duplicate the analog and HDMI output but
there is, however, a slight delay of the HDMI audio.

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start set-turntable-loopback-sound.service``

Enable
......

``# systemctl enable set-turntable-loopback-sound.service``

Licenses
~~~~~~~~

- CC-BY-SA 3.0

YAML data
~~~~~~~~~


::


    <--YAML-->
    archive_documents_simple.sh:
        category: archiving
        running user: mydesktopuser
        configuration files:
            paths:
                - set-turntable-loopback-sound.asoundrc
        systemd unit files:
            paths:
                service:
                    - set-turntable-loopback-sound.service
    <!--YAML-->


----

Video
-----

record_motion.sh
````````````````

Purpose
~~~~~~~

I use this script to record video streams captured by webcams
with `Motion <https://motion-project.github.io/>`_. 

.. important:: We will assume that Motion is already configured and running.

Steps
~~~~~

1. make sure to have a *big enough* hard drive

References
~~~~~~~~~~

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
| GNU Coreutils        | - mkdir    | 8.31             |
|                      | - rm       |                  |
+----------------------+------------+------------------+
| FFmpeg               | - ffmpeg   | 1:4.2.1          |
+----------------------+------------+------------------+
| Findutils            | - find     | 4.7.0            |
+----------------------+------------+------------------+

Configuration files
~~~~~~~~~~~~~~~~~~~

Systemd unit files
~~~~~~~~~~~~~~~~~~

Deploy commands
~~~~~~~~~~~~~~~

Start
.....

``# systemctl start record-motion.camera1.service``

Enable
......

``# systemctl enable record-motion.camera1.service``

Licenses
~~~~~~~~

- GPLv3+

YAML data
~~~~~~~~~


::


    <--YAML-->
    record_motion.sh:
        category: video
        running user: surveillance
        configuration files:
            paths:
                - record_motion.camera1.conf
        systemd unit files:
            paths:
                service:
                    - record-motion.camera1.service
    <!--YAML-->

