#!/usr/bin/env python3
#
# extract_gpx_data_from_dashcams.py
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
r"""Generate GPX files from embedded EXIF metadata in videos."""

import filecmp
import fpyutils
import sys
import shlex
import pathlib
import datetime

if __name__ == '__main__':
    configuration_file = shlex.quote(shlex.quote(sys.argv[1]))
    config = fpyutils.yaml.load_configuration(configuration_file)

    processed_gpx_files = list()
    removed_video_files = list()
    corrupt_video_files = list()
    removed_duplicate_gpx_files = list()

    for f in sorted(
            pathlib.Path(shlex.quote(config['files']['root dir'])).glob(
                config['files']['video globbing pattern'])):
        if f.is_file() and (
                datetime.date.today() -
                datetime.date.fromtimestamp(f.stat().st_mtime)
        ).days > config['files']['process files older than days']:
            print('Processing ' + str(f) + '...')
            command = 'exiftool -extractEmbedded ' + str(f)
            if fpyutils.shell.execute_command_live_output(command) == 0:
                command = 'exiftool -extractEmbedded -printFormat ' + shlex.quote(
                    config['files']['gpx template file']) + ' ' + str(
                        f) + ' > ' + str(f) + '.gpx'
                fpyutils.shell.execute_command_live_output(command)
                processed_gpx_files.append(str(f) + '.gpx')
                print('OK')
                if config['remove']['processed files']:
                    f.unlink()
                    removed_video_files.append(str(f))
            else:
                corrupt_video_files.append(str(f))
                if config['remove']['corrupt files']:
                    f.unlink()
                    removed_video_files.append(str(f))
                print('KO')

    pgf = len(processed_gpx_files)
    if config['remove']['duplicate gpx files'] and pgf > 0:
        i = 0
        go = True
        keep = list()
        j = len(processed_gpx_files)
        while go:
            alpha = processed_gpx_files.pop(i)
            keep.append(alpha)

            g2 = True
            if len(processed_gpx_files) == 0:
                g2 = False

            j = 0
            while g2:
                if filecmp.cmp(alpha, processed_gpx_files[j]):
                    to_delete = processed_gpx_files.pop(j)
                    pathlib.Path(to_delete).unlink()
                    removed_duplicate_gpx_files.append(to_delete)
                else:
                    j += 1

                if j == len(processed_gpx_files):
                    g2 = False

            if i == len(processed_gpx_files):
                go = False

    message = ('processed gpx files: ' + str(pgf) + '\n' +
               'removed video files: ' + str(len(removed_video_files)) + '\n' +
               'corrupt video files: ' + str(len(corrupt_video_files)) + '\n' +
               'removed duplicate gpx files :' +
               str(len(removed_duplicate_gpx_files)) + '\n')

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
