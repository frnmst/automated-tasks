#!/usr/bin/env python3
#
# smartd_test.py
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
r"""Run S.M.A.R.T tests on hard drives."""

import fpyutils
import re
import configparser
import sys
import os
import pathlib
import subprocess
import json
import shlex

# Constants.
# These need to be checked.
STATUS_IDLE = 0
STATUS_BUSY = 249

# You must stop programs like hd-idle before performing these tests.


class UserNotRoot(Exception):
    """The user running the script is not root."""


class NoDisksConfigured(Exception):
    """No disks configured."""


def get_disks() -> list:
    r"""Scan all the disks."""
    disks = list()
    for d in pathlib.Path('/dev/disk/by-id').iterdir():
        # Ignore disks ending with part-${integer} to avoid duplicates (names
        # corresponding to partitions of the same disk).
        disk = str(d)
        if re.match('.+-part[0-9]+$', disk) is None:
            try:
                ddict = json.loads(
                    subprocess.run(shlex.split('smartctl --all --json ' +
                                               shlex.quote(disk)),
                                   capture_output=True,
                                   check=True,
                                   timeout=30).stdout)
                try:
                    # Check for smart test support.
                    if ddict['ata_smart_data']['capabilities'][
                            'self_tests_supported']:
                        disks.append(disk)
                except KeyError:
                    pass
            except subprocess.TimeoutExpired:
                print('timeout for ' + disk)
            except subprocess.CalledProcessError:
                print('device ' + disk +
                      ' does not support S.M.A.R.T. commands, skipping...')

    return disks


def disk_ready(disk: str) -> bool:
    r"""Check if the disk is ready."""
    # Raises a KeyError if disk has not S.M.A.R.T. status capabilities.
    ddict = json.loads(
        subprocess.run(shlex.split('smartctl --all --json ' +
                                   shlex.quote(disk)),
                       capture_output=True,
                       check=True,
                       timeout=30).stdout)
    if ddict['ata_smart_data']['self_test']['status']['value'] != STATUS_BUSY:
        return True
    else:
        return False


def run_test(disk: str, test_length: str = 'long') -> str:
    r"""Run the smartd test."""
    return subprocess.run(
        shlex.split('smartctl --test=' + shlex.quote(test_length) + ' ' +
                    shlex.quote(disk)),
        capture_output=True,
        check=True,
        timeout=30).stdout


if __name__ == '__main__':
    if os.getuid() != 0:
        raise UserNotRoot

    configuration_file = shlex.quote(sys.argv[1])
    config = configparser.ConfigParser()
    config.read(configuration_file)

    # Do not prepend '/dev/disk/by-id/'.
    disks_to_check = shlex.quote(sys.argv[2])
    disks_available = get_disks()

    if len(config.sections()) == 0:
        raise NoDisksConfigured

    for s in config.sections():
        dev = '/dev/disk/by-id/' + s
        if config.getboolean(s, 'enable') and dev in disks_available:
            if disks_to_check == 'all' or disks_to_check == s:
                if disk_ready(dev):
                    print('attempting ' + s + ' ...')
                    message = run_test(dev, config[s]['test']).decode('utf-8')
                    print(message)
                    if config.getboolean(s, 'log to gotify'):
                        fpyutils.notify.send_gotify_message(
                            config[s]['gotify url'], config[s]['gotify token'],
                            message, config[s]['gotify title'],
                            int(config[s]['gotify priority']))
                else:
                    # Drop test requests if a disk is running a test in a particular moment.
                    # This avoid putting the disks under too much stress.
                    print('disk ' + s + ' not ready, checking the next...')
