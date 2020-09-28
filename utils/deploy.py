#!/usr/bin/env python3
#
# deploy.py
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
r"""Deploy the unit files."""

import shutil
import os
import pathlib
import subprocess
import shlex
import fpyutils

SRC_DIR = '/home/jobs/services/by-user'
DST_DIR = '/etc/systemd/system'


class UserNotRoot(Exception):
    r"""The user running the script is not root."""


def get_unit_files(start_dir: str = '.', max_depth: int = 0) -> tuple:
    r"""Get the file names of the unit files."""
    timers = list()
    services = list()
    p = pathlib.Path(start_dir)

    # A file has a fake depth of 1 even if we are at level 0 of the directory tree.
    # The reason of this is how the depth is computed below.
    max_depth += 1

    # Match files and directories.
    for f in p.rglob('*'):
        if f.is_file() and len(
                pathlib.PurePath(f.relative_to(
                    pathlib.PurePath(start_dir))).parts) <= max_depth:
            if pathlib.PurePath(f).match('*.timer'):
                timers.append(f)
            if pathlib.PurePath(f).match('*.service'):
                services.append(f)

    return timers, services


def copy_unit_files(unit_files: list, dst_dir: str = DST_DIR):
    r"""Copy multiple unit files."""
    for f in unit_files:
        shutil.copyfile(
            str(f), str(pathlib.Path(shlex.quote(dst_dir),
                                     shlex.quote(f.name))))


def start_and_enable_unit(unit_name: str, unit_type: str):
    r"""Start and enable services or timers."""
    if unit_type not in ['service', 'timer']:
        raise ValueError

    print('unit: ' + unit_name + '.' + unit_type)
    o1 = subprocess.run(shlex.split('systemctl enable ' +
                                    shlex.quote(unit_name) + '.' + unit_type),
                        check=True,
                        capture_output=True).stderr.decode('UTF-8').strip()
    if o1 != str():
        print(o1)

    status = subprocess.run(
        shlex.split('systemctl is-enabled ' + shlex.quote(unit_name) + '.' +
                    unit_type),
        check=True,
        capture_output=True).stdout.decode('UTF-8').strip()
    disable = True
    if status in ['enabled', 'enabled-runtime']:
        disable = False
    elif status in ['static']:
        # Completely disable units without the '[Install]' section.
        disable = True

    if disable:
        try:
            o2 = subprocess.run(
                shlex.split('systemctl stop ' + shlex.quote(unit_name) + '.' +
                            unit_type),
                check=True,
                capture_output=True).stderr.decode('UTF-8').strip()
            if o2 != str():
                print(o2)
            o3 = subprocess.run(
                shlex.split('systemctl disable ' + shlex.quote(unit_name) +
                            '.' + unit_type),
                check=True,
                capture_output=True).stderr.decode('UTF-8').strip()
            if o3 != str():
                print(o3)
        except subprocess.CalledProcessError:
            # A new template unit, the ones with 'name@.service' as filename,
            # without the '[Install]' section cannot be stopped nor disabled.
            # See https://wiki.archlinux.org/index.php/Systemd#Using_units
            pass
    else:
        o2 = subprocess.run(
            shlex.split('systemctl start ' + shlex.quote(unit_name) + '.' +
                        unit_type),
            check=True,
            capture_output=True).stderr.decode('UTF-8').strip()
        if o2 != str():
            print(o2)


def start_and_enable_units(services: list, timers: list):
    r"""Start and enable all services and timers."""
    # Not all services have timer files but all timers have service files.
    # For these cases start and enable the service instead of the timer file.
    diff = list(set(services) - set(timers))
    for d in diff:
        start_and_enable_unit(d, 'service')
    for t in timers:
        start_and_enable_unit(t, 'timer')


def get_file_names_from_paths(unit_files: list):
    r"""Get a relative paths from absolute paths."""
    names = list()
    for u in unit_files:
        names.append(u.name)
    return names


def remove_file_extensions(unit_files: list):
    r"""Remove extension from file names."""
    names = list()
    for u in unit_files:
        names.append(pathlib.PurePath(u.stem))
    return names


if __name__ == '__main__':
    if os.getuid() != 0:
        raise UserNotRoot

    new_timers, new_services = get_unit_files(SRC_DIR, 1)
    copy_unit_files(new_timers, DST_DIR)
    copy_unit_files(new_services, DST_DIR)

    fpyutils.shell.execute_command_live_output('systemctl daemon-reload')
    fpyutils.shell.execute_command_live_output('systemctl reset-failed')

    services = get_file_names_from_paths(remove_file_extensions(new_services))
    timers = get_file_names_from_paths(remove_file_extensions(new_timers))
    start_and_enable_units(services, timers)
