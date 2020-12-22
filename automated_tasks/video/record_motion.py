#!/usr/bin/env python3
#
# record_motion.py
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
r"""Record motion camera videos."""

import fpyutils
import sys
import shlex
import pathlib
import datetime

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    try:
        message = 'started recording motion camera: ' + config['camera name'] + '\n'
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
    except Exception as e:
        # Ignore errors.
        print(e)

    if config['ffmpeg']['use global quality']:
        quality_string = '-global_quality ' + config['ffmpeg']['global quality']
    else:
        quality_string = '-q:v ' + config['ffmpeg']['quality']

    pathlib.Path(config['dst directory']).mkdir(parents=True, exist_ok=True)
    while True:
        # Delete videos older than 'days to keep' days.
        for d in pathlib.Path(config['dst directory']).iterdir():
            # Work with naive datetime objects because we assume
            # that everyting is handled on the same computer.
            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(d.stat().st_mtime)).total_seconds() > config['seconds to keep']:
                d.unlink()

        # Record the video as a motion JPEG incapsulated in a Martoska file.
        # Usually this script is run on the same computer handling the video
        # stream.
        video_path = str(pathlib.Path(config['dst directory'], 'video_' + str(datetime.datetime.now().strftime('%F_%T')) + '.mkv'))
        command = (
            config['ffmpeg']['executable']
            + ' ' + config['ffmpeg']['extra options pre']
            + ' -an '
            + ' -i ' + config['url']
            + ' ' + quality_string
            + ' -video_size ' + config['ffmpeg']['video size']
            + ' -c:v ' + config['ffmpeg']['video codec']
            + ' -vframes ' + config['ffmpeg']['frames per file']
            + ' ' + config['ffmpeg']['extra options post']
            + ' ' + video_path
        )
        fpyutils.shell.execute_command_live_output(command, dry_run=False)
