#!/usr/bin/env python3
#
# youtube_dl.py
#
# Copyright (C) 2019-2020 Franco Masotti <franco.masotti@live.com>
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
r"""Download videos, delete old ones and get a notification."""

import pathlib
import fpyutils
import datetime
import shlex
import sys

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    pathlib.Path(config['youtube dl']['dst dir']).mkdir(mode=0o700,
                                                        parents=True,
                                                        exist_ok=True)
    pathlib.Path(config['youtube dl']['archived list file']).touch(
        mode=0o700, exist_ok=True)
    original_files = sum(
        1 for line in open(config['youtube dl']['archived list file']))

    # youtube-dl might not return 0 even if some videos are correctly downloaded.
    command = 'pushd ' + config['youtube dl'][
        'dst dir'] + ' ; youtube-dl --verbose --config-location ' + config[
            'youtube dl']['options file'] + ' --batch ' + config['youtube dl'][
                'url list file'] + ' --download-archive ' + config[
                    'youtube dl']['archived list file'] + ' ; popd'
    fpyutils.shell.execute_command_live_output(command)

    # For this to work be sure to set the no-mtime option in the options file.
    # Only the video files, infact, would retain the original modification time
    # (not the modification time correpsponding to the download time).
    # All the other files such as thumbnails and subtitles do not retain the
    # original mtime. For this reason it is simpler not to consider the
    # original mtime.
    deleted_files = 0
    if config['delete']['enabled']:
        for f in sorted(
                pathlib.Path(config['youtube dl']['dst dir']).glob('*/*')):
            if f.is_file() and (datetime.date.today() -
                                datetime.date.fromtimestamp(f.stat().st_mtime)
                                ).days > config['delete']['days to keep']:
                f.unlink()
                deleted_files += 1

    final_files = sum(
        1 for line in open(config['youtube dl']['archived list file']))

    downloaded_files = final_files - original_files

    message = 'DW: ' + str(downloaded_files) + ' ; RM: ' + str(deleted_files)
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
