#!/usr/bin/env python3
#
# notify_unit_status.py
#
# Copyright (C) 2015 Pablo Martinez @ Stack Exchange (https://serverfault.com/a/701100)
# Copyright (C) 2018 Davy Landman @ Stack Exchange (https://serverfault.com/a/701100)
# Copyright (C) 2020 Franco Masotti <franco.masotti@live.com>
#
# This script is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
r"""Send a notification when a Systemd unit fails."""

import fpyutils
import shlex
import sys

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    failed_unit = shlex.quote(sys.argv[2])

    message = 'service failure: ' + failed_unit
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
