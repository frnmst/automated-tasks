#!/usr/bin/env python3
#
# archive_emails.py
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php/OfflineIMAP
# Copyright (C)  2019-2020  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".
#
# See also https://github.com/OfflineIMAP/offlineimap/blob/master/offlineimap.conf
r"""Save emails."""

import subprocess
import shlex
import re
import fpyutils
import sys

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    command = 'offlineimap -u machineui -c ' + shlex.quote(
        config['files']['offlineimap config'])
    r = subprocess.run(shlex.split(command), capture_output=True, shell=False)
    stdout = r.stdout.decode('UTF-8')
    copied_emails = len(
        re.findall(config['operations']['copied emails regex'], stdout,
                   re.MULTILINE))
    print(stdout)

    if r.returncode == 0:
        message = 'no errors\n'
    else:
        message = 'errors\n'

    message += 'copied: ' + str(copied_emails)
    print(message)
    if config['notify']['gotify']['enabled']:
        m = config['notify']['gotify']['message'] + '\n' + message
        fpyutils.notify.send_gotify_message(
            config['notify']['gotify']['url'],
            config['notify']['gotify']['token'], m,
            config['notify']['gotify']['title'],
            config['notify']['gotify']['priority'])
    if config['notify']['email']['enabled']:
        fpyutils.notify.send_email(message,
                                   config['notify']['email']['smtp server'],
                                   config['notify']['email']['port'],
                                   config['notify']['email']['sender'],
                                   config['notify']['email']['user'],
                                   config['notify']['email']['password'],
                                   config['notify']['email']['receiver'],
                                   config['notify']['email']['subject'])
