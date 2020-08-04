#!/usr/bin/env python3
#
# notify_camera_actions.py
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
r"""Send notifications when something happens to a motion camera."""

import fpyutils
import sys
import shlex

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)
    camera_name = shlex.quote(sys.argv[2])
    action = shlex.quote(sys.argv[3])

    message = 'motion\n' + 'camera: ' + camera_name + '\n' + 'action: ' + action
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
