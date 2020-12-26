#!/usr/bin/env python3
#
# clean_pacman.py
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php/Pacman
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php/Pacman/Tips_and_tricks
# Copyright (C)  2019-2020  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".
r"""Clean pacman cache."""

import fpyutils
import shlex
import sys

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    # Remove cache of uninstalled and installed programs keeping previous x pkgs.
    command = 'paccache --remove --keep ' + config['previous package versions to keep'] + ' --verbose --verbose --verbose'
    fpyutils.shell.execute_command_live_output(command, dry_run=False)

    # Remove all cache of uninstalled packages.
    command = 'paccache --remove --keep 0 --uninstalled --verbose --verbose --verbose'
    fpyutils.shell.execute_command_live_output(command, dry_run=False)

    # Select orphan packages. and remove them.
    command = 'pacman --remove --nosave --recursive $(pacman --query --unrequired --deps --quiet) --noconfirm --verbose'
    fpyutils.shell.execute_command_live_output(command, dry_run=False)

    message = 'cleaned pacman cache'
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
