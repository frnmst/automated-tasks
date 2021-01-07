#!/usr/bin/env python3
#
# save_and_notify_file_diffs.py
#
# Copyright (C) 2021 Franco Masotti <franco.masotti@live.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
r"""Send notifications and save files if remotes change."""

import fpyutils
import requests
import pathlib
import sys
import shlex
import hashlib
import urllib.parse

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    # Assume to be in the correct directory.

    vcs_base_command = config['vcs']['executable'] + ' ' + config['vcs']['directory option'] + ' ' + config['files']['repository full path']

    # Check if directory is git repository.
    if fpyutils.shell.execute_command_live_output(vcs_base_command + ' ' + config['vcs']['commands']['check repo']) == 0:
        fpyutils.shell.execute_command_live_output(vcs_base_command + ' ' + config['vcs']['commands']['pull'])
        files_changed = 0
        to_commit = False
        for url in config['urls']:
            try:
                r = requests.get(url)
                components = urllib.parse.urlsplit(url)
                if components.path == str():
                    # Save using default name like wget.
                    # Note: duplicate files are not considered.
                    file_name = components.netloc + '_' + config['files']['default name suffix']
                else:
                    file_name = pathlib.Path(components.path).name

                # Compute checksums. This is not necessary if using a VCS
                # like git.
                m = hashlib.sha512()
                m.update(bytes(r.text, 'UTF-8'))
                requests_checksum = m.hexdigest()
                file_exists = False
                full_path_file = str(pathlib.Path(config['files']['repository full path'], file_name))
                if pathlib.Path(full_path_file).is_file():
                    n = hashlib.sha512()
                    n.update(open(full_path_file, 'rb').read())
                    existing_checksum = n.hexdigest()
                    file_exists = True

                if not file_exists or requests_checksum != existing_checksum:
                    new_checksum = requests_checksum
                    files_changed += 1

                    # Write the new file.
                    with open(full_path_file, 'w') as f:
                        f.write(r.text)

                    # Track the file.
                    fpyutils.shell.execute_command_live_output(vcs_base_command + ' ' + config['vcs']['commands']['add'] + ' ' + shlex.quote(file_name))
                    to_commit = True

                    message = 'new checksum for ' + file_name + ': ' + new_checksum
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

            except requests.exceptions.RequestException as e:
                print(e)

        if to_commit:
            fpyutils.shell.execute_command_live_output(vcs_base_command + ' ' + config['vcs']['commands']['commit'] + ' ' + shlex.quote('"' + str(files_changed) + ' files added."'))
            fpyutils.shell.execute_command_live_output(vcs_base_command + ' ' + config['vcs']['commands']['push'])
            message = 'total files changed: ' + str(files_changed)
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
