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

+----------------------+------------+------------------+----------------------------------------------------+
| Name                 | Binaries   | Version          | Homepage                                           |
+======================+============+==================+====================================================+
| GNU Bash             | - bash     | 5.0.7(1)         | http://www.gnu.org/software/bash/bash.html         |
+----------------------+------------+------------------+----------------------------------------------------+
| Findutils            | - find     | 4.6.0            | https://www.gnu.org/software/findutils/            |
+----------------------+------------+------------------+----------------------------------------------------+
| Gawk                 | - gawk     | 4.2.1            | http://www.gnu.org/software/gawk/                  |
+----------------------+------------+------------------+----------------------------------------------------+
| GNU Coreutils        | - chmod    | 8.31             | https://www.gnu.org/software/coreutils/            |
|                      | - cp       |                  |                                                    |
|                      | - date     |                  |                                                    |
|                      | - printf   |                  |                                                    |
|                      | - rm       |                  |                                                    |
|                      | - sha1sum  |                  |                                                    |
|                      | - sha512sum|                  |                                                    |
|                      | - sort     |                  |                                                    |
|                      | - sync     |                  |                                                    |
|                      | - tr       |                  |                                                    |
+----------------------+------------+------------------+----------------------------------------------------+
| Ghostscript          | - gs       | 9.27             | https://www.ghostscript.com/                       |
+----------------------+------------+------------------+----------------------------------------------------+
| OCRmyPDF             | - ocrmypdf | 8.3.0            | https://github.com/jbarlow83/OCRmyPDF              |
+----------------------+------------+------------------+----------------------------------------------------+

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


