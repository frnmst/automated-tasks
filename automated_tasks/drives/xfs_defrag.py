#!/usr/bin/env python3
#
# xfs_defrag.py
#
# Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>
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

import fpyutils
import subprocess
import shlex
import os
import configparser
import sys
import json

# See https://brashear.me/blog/2017/07/30/adventures-in-xfs-defragmentation/

# Fields are space separated strings. Field Ids start with an id of 0.
FIELD_ID_ACTUAL = 1
FIELD_ID_IDEAL = 3
TEXT_ENCODING = 'UTF-8'
PARTITION_BASE_PATH = '/dev/disk/by-uuid/'
LINE_SEPARATOR = '\n'


class UserNotRoot(Exception):
    """The user running the script is not root."""


def get_frag_status(filesystem: str) -> str:
    return subprocess.run(
        shlex.split('xfs_db -c frag -r ' + PARTITION_BASE_PATH +
                    shlex.quote(filesystem)),
        capture_output=True).stdout.decode(TEXT_ENCODING)


def compute_frag_status(out: str) -> float:
    # Get the first line only.
    out = out.split(LINE_SEPARATOR)
    out = out[0]

    # It is a phrase so fields are separated by a whitespace.
    out = out.split(' ')

    # Get the correct fields and remove the final ',' character.
    actual = int(out[FIELD_ID_ACTUAL][:-1])
    ideal = int(out[FIELD_ID_IDEAL][:-1])

    optimization = actual / ideal
    frag_factor_percent = (abs(1 - optimization)) * 100

    return frag_factor_percent


def defrag_needs_to_be_executed(frag_threshold_percent: float,
                                frag_factor_percent: float) -> bool:
    execute = False
    if frag_factor_percent >= frag_threshold_percent:
        execute = True
    return execute


def run_defrag(filesystem: str, timeout_seconds: int):
    return subprocess.run(
        shlex.split('xfs_fsr -v -t ' + shlex.quote(str(timeout_seconds)) +
                    ' ' + PARTITION_BASE_PATH + shlex.quote(filesystem)),
        capture_output=True).stdout.decode(TEXT_ENCODING)


def get_filesystems(filesystem_type: str = 'xfs') -> str:
    r"""Filter available filesystem by type and get their uuid."""
    filesystem_uuids = list()
    s = subprocess.run(
        shlex.split('lsblk --json --tree --inverse --output uuid,fstype'),
        capture_output=True).stdout.decode(TEXT_ENCODING)
    j = json.loads(s)
    for i in range(0, len(j['blockdevices'])):
        if j['blockdevices'][i]['fstype'] == filesystem_type:
            filesystem_uuids.append(j['blockdevices'][i]['uuid'])
    return filesystem_uuids


if __name__ == '__main__':
    if os.getuid() != 0:
        raise UserNotRoot

    configuration_file = shlex.quote(sys.argv[1])
    config = configparser.ConfigParser()
    config.read(configuration_file)

    # Do not prepend '/dev/disk/by-uuid/'.
    filesystem_uuids_to_check = shlex.quote(sys.argv[2])
    filesystem_uuids_available = get_filesystems()

    for s in config.sections():
        if s in filesystem_uuids_available and filesystem_uuids_to_check == s:
            frag_status = get_frag_status(s)
            message = 'before\n' + frag_status
            print(frag_status)
            if defrag_needs_to_be_executed(
                    float(config[s]['fragmentation threshold percent']),
                    compute_frag_status(frag_status)):
                print(run_defrag(s, int(config[s]['timeout'])))
                message += '\nafter\n' + get_frag_status(s)
                print(get_frag_status(s))
            if config.getboolean(s, 'log to gotify'):
                fpyutils.gotify.send_gotify_message(
                    config[s]['gotify url'], config[s]['gotify token'],
                    config[s]['gotify message'] + '\n\n' + message,
                    config[s]['gotify title'],
                    int(config[s]['gotify priority']))
