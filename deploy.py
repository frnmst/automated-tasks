#!/usr/bin/env python3

import shutil
import configparser
import os
import pathlib
import subprocess
import json
import shlex

SRC_DIR='/home/jobs/services/by-user'
DST_DIR='/etc/systemd/system'

class UserNotRoot(Exception):
    """The user running the script is not root."""

def get_unit_files(start_dir: str='.', max_depth=0):
    timers = list()
    services = list()
    p = pathlib.Path(start_dir)

    # A file has a fake depth of 1 even if we are at level 0 of the directory tree.
    # The reason of this is how the depth is computed below.
    max_depth += 1

    # Match files and directories.
    for f in p.rglob('*'):
        if f.is_file() and len(pathlib.PurePath(f.relative_to(pathlib.PurePath(start_dir))).parts) <= max_depth:
            if pathlib.PurePath(f).match('*.timer'):
                timers.append(f)
            if pathlib.PurePath(f).match('*.service'):
                services.append(f)

    return timers, services

def copy_unit_files(unit_files: list, dst_dir: str=DST_DIR):
    for f in unit_files:
        shutil.copyfile(str(f), dst_dir + '/' + f.name)

def reload_systemd_daemon():
    subprocess.run(shlex.split('systemctl daemon-reload'),check=True,capture_output=True)

def start_and_enable_units(services: list, timers: list):
    # Not all services have timer files.
    # For these cases start and enable the service instead of the timer file.
    diff = list(set(services) - set(timers))
    for d in diff:
        o1 = subprocess.run(shlex.split('systemctl enable ' + shlex.quote(d) + '.service'),check=True,capture_output=True).stderr.decode('utf-8').strip()
        if o1 != '':
            print (o1)
        o2 = subprocess.run(shlex.split('systemctl start ' + shlex.quote(d) + '.service'),check=True,capture_output=True).stderr.decode('utf-8').strip()
        if o2 != '':
            print (o2)
    for t in timers:
        o3 = subprocess.run(shlex.split('systemctl enable ' + shlex.quote(t) + '.timer'),check=True,capture_output=True).stderr.decode('utf-8').strip()
        if o3 != '':
            print (o3)
        o4 = subprocess.run(shlex.split('systemctl start ' + shlex.quote(t) + '.timer'),check=True,capture_output=True).stderr.decode('utf-8').strip()
        if o4 != '':
            print (o4)

def get_file_names_from_paths(unit_files: list):
    names = list()
    for u in unit_files:
        names.append(u.name)
    return names

def remove_file_extensions(unit_files: list):
    names = list()
    for u in unit_files:
        names.append(pathlib.PurePath(u.stem))
    return names

if __name__ == '__main__':
    if os.getuid() != 0:
        raise UserNotRoot

    existing_timers, existing_services = get_unit_files(DST_DIR, 0)
    new_timers, new_services = get_unit_files(SRC_DIR, 1)
    copy_unit_files(new_timers, DST_DIR)
    copy_unit_files(new_services, DST_DIR)

    reload_systemd_daemon()

    services = get_file_names_from_paths(remove_file_extensions(new_services))
    timers = get_file_names_from_paths(remove_file_extensions(new_timers))
    start_and_enable_units(services, timers)

