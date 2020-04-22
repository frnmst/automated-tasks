References
==========

Common commands
---------------

+----+----------------------------------------------+------------------------------------------------------------------------+
| Id | Description                                  | Command                                                                |
+====+==============================================+========================================================================+
| 0  | create a user,                               | ::                                                                     |
|    | group and its home                           |                                                                        |
|    |                                              |     # useradd --create-home --shell /bin/bash --user-group ${username} |
|    |                                              |                                                                        |
+----+----------------------------------------------+------------------------------------------------------------------------+
| 1  | install                                      |                                                                        |
|    | `Gotify <https://github.com/gotify/server>`_ |                                                                        |
|    | and run an instance                          |                                                                        |
+----+----------------------------------------------+------------------------------------------------------------------------+
| 2  | create a system user and its group           | ::                                                                     |
|    |                                              |                                                                        |
|    |                                              |     # useradd --system --shell /bin/bash --user-group ${username}      |
|    |                                              |                                                                        |
+----+----------------------------------------------+------------------------------------------------------------------------+

List of software
----------------

==============================    =========================================================
Software name                     Homepage
==============================    =========================================================
alsa-utils                        http://www.alsa-project.org
aria2                             http://aria2.sourceforge.net/
BeautifulSoup                     https://www.crummy.com/software/BeautifulSoup/index.html
borgmatic                         https://torsion.org/borgmatic/
curl                              https://curl.haxx.se
dateutil                          https://github.com/dateutil/dateutil
Document Scanner                  https://gitlab.gnome.org/GNOME/simple-scan
exiftool                          http://search.cpan.org/perldoc?exiftool
fattura-elettronica-reader        https://github.com/frnmst/fattura-elettronica-reader/
feh                               https://feh.finalrewind.org/
FFmpeg                            https://ffmpeg.org/
Findutils                         https://www.gnu.org/software/findutils/
Gawk                              http://www.gnu.org/software/gawk/
Ghostscript                       https://www.ghostscript.com/
Git                               https://git-scm.com/
Gitea                             https://gitea.io/en-us/
GNU Bash                          http://www.gnu.org/software/bash/bash.html
GNU C Library                     https://www.gnu.org/software/libc
GNU Coreutils                     https://www.gnu.org/software/coreutils/
GNU Grep                          https://www.gnu.org/software/grep/
GNU Make                          http://www.gnu.org/software/make
GNU Parallel                      https://www.gnu.org/software/parallel/
GNU Screen                        https://www.gnu.org/software/screen
hblock                            https://github.com/hectorm/hblock
JBIG2 Encoder                     https://github.com/agl/jbig2enc
Khal                              https://lostpackets.de/khal/
Kiwix tools                       https://github.com/kiwix/kiwix-tools
lxml                              https://lxml.de/
Msmtp                             https://marlam.de/msmtp/
OCRmyPDF                          https://github.com/jbarlow83/OCRmyPDF
OfflineIMAP                       http://offlineimap.org/
OpenSSH                           https://www.openssh.com/portable.html
pacman-contrib                    https://git.archlinux.org/pacman-contrib.git/about/
pycups                            http://cyberelk.net/tim/software/pycups/
Primitive FTPd                    https://github.com/wolpi/prim-ftpd
Python                            http://www.python.org/
Python-LLFUSE                     https://github.com/python-llfuse/python-llfuse/
PyYAML                            https://pyyaml.org/wiki/PyYAML
Radicale                          https://radicale.org
Requests                          http://python-requests.org
rsync                             https://rsync.samba.org/
RTorrent                          https://rakshasa.github.io/rtorrent/
S-nail                            https://www.sdaoden.eu/code.html#s-nail
shadow                            https://github.com/shadow-maint/shadow
Smartmontools                     http://smartmontools.sourceforge.net
sudo                              https://www.sudo.ws/sudo/
systemd                           https://www.github.com/systemd/systemd
Tesseract OCR                     https://github.com/tesseract-ocr/tesseract
Todoman                           https://github.com/pimutils/todoman
util-linux                        https://github.com/karelzak/util-linux
Vdirsyncer                        https://vdirsyncer.pimutils.org/en/stable/
WeasyPrint                        http://weasyprint.org/
Xorg                              https://xorg.freedesktop.org/
YaCy                              https://github.com/yacy/yacy_search_server
youtube-dl                        https://ytdl-org.github.io/youtube-dl/
==============================    =========================================================

List of licenses
----------------

=================    ============================================================
License name         Homepage
=================    ============================================================
BSD                  https://opensource.org/licenses/BSD-3-Clause
CC-BY-SA 2.5         https://creativecommons.org/licenses/by-sa/2.5/
CC-BY-SA 3.0         https://creativecommons.org/licenses/by-sa/3.0/
CC-BY-SA 4.0         https://creativecommons.org/licenses/by-sa/4.0/
GFDLv1.3+            https://www.gnu.org/licenses/fdl-1.3.en.html
GPLv2+               https://www.gnu.org/licenses/gpl-2.0.html
GPLv3+               https://www.gnu.org/licenses/gpl-3.0.html
LGPLv2+              https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
MIT                  https://opensource.org/licenses/MIT
=================    ============================================================

List of running users
---------------------

===================   ======================================================================================
User name             Description
===================   ======================================================================================
``command-assert``    a user that runs specific commands
``email``             a user that sends emails
``gitea``             the user running a `Gitea <https://gitea.io/en-us/>`_ instance
``kiwix``             a user running the Kiwix server
``motion``            the user running a `Motion <https://motion-project.github.io/index.html>`_ instance
``mydesktopuser``     a generic user with Xorg access
``myuser``            a generic user with our without Xorg access
``root``              the root user
``rtorrent``          the user running an `RTorrent <https://rakshasa.github.io/rtorrent/>`_ instance
``surveillance``      a user running audio and/or video surveillance scripts or programs
``yacy``              the user running a `YaCy <https://www.yacy.net/>`_ instance
===================   ======================================================================================

List of programming languages
-----------------------------

==============        ==================================
Name                  Homepage
==============        ==================================
bash                  TODO
perl                  TODO
python                TODO
==============        ==================================
