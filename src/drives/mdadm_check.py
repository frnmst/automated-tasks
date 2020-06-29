#!/usr/bin/env python3

# Copyright (C) 2014-2017 Neil Brown <neilb@suse.de>
#
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    Author: Neil Brown
#    Email: <neilb@suse.com>
#
# Copyright (C) 2019-2020 Franco Masotti <franco.masotti@live.com>

import fpyutils
import configparser
import sys
import time
import os
import multiprocessing
import pathlib
import collections

# Constants.
STATUS_CLEAN = 'clean'
STATUS_ACTIVE = 'active'
STATUS_IDLE = 'idle'


class UserNotRoot(Exception):
    """The user running the script is not root."""


class NoAvailableArrays(Exception):
    """No available arrays."""


class NoSelectedArraysPresent(Exception):
    """None of the arrays in the configuration file exists."""


def get_active_arrays():
    active_arrays = list()
    with open('/proc/mdstat', 'r') as f:
        line = f.readline()
        while line:
            if STATUS_ACTIVE in line:
                active_arrays.append(line.split()[0])
            line = f.readline()

    return active_arrays


def get_array_state(array: str):
    return open('/sys/block/' + array + '/md/array_state', 'r').read().rstrip()


def get_sync_action(array: str):
    return open('/sys/block/' + array + '/md/sync_action', 'r').read().rstrip()


def run_action(array: str, action: str):
    with open('/sys/block/' + array + '/md/sync_action', 'w') as f:
        f.write(action)


def main_action(array: str, notify_enabled: bool, notify: dict):
    action = devices[array]
    go = True
    while go:
        if get_sync_action(array) == STATUS_IDLE:
            message = 'running ' + action + ' on /dev/' + array + '. pid: ' + str(
                os.getpid())
            run_action(array, action)
            message += '\n\n'
            message += 'finished pid: ' + str(os.getpid())
            print(message)
            if notify_enabled:
                fpyutils.notify.send_gotify_message(
                    notify['gotify url'], notify['gotify token'], message,
                    notify['gotify title'], int(notify['gotify priority']))
            go = False
        if go:
            print('waiting ' + array + ' to be idle...')
            time.sleep(timeout_idle_check)


if __name__ == '__main__':
    if os.getuid() != 0:
        raise UserNotRoot

    configuration_file = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(configuration_file)
    max_concurrent_checks = int(config['DEFAULT']['max concurrent checks'])
    timeout_idle_check = int(config['DEFAULT']['timeout idle check'])
    devices = dict()
    for dev in config['devices']:
        devices[dev] = config['devices'][dev]
    notify_enabled = config.getboolean('notify', 'log to gotify')
    notify = config['notify']

    active_arrays = get_active_arrays()
    dev_queue = collections.deque()
    if len(active_arrays) > 0:
        for dev in active_arrays:
            if pathlib.Path('/sys/block/' + dev + '/md/sync_action').is_file():
                state = get_array_state(dev)
                if state == STATUS_CLEAN or state == STATUS_ACTIVE or state == STATUS_IDLE:
                    try:
                        if devices[dev] != 'ignore' and dev in devices:
                            dev_queue.append(dev)
                    except KeyError:
                        pass

    if len(active_arrays) == 0:
        raise NoAvailableArrays
    if len(dev_queue) == 0:
        raise NoSelectedArraysPresent

    while len(dev_queue) > 0:
        for i in range(0, max_concurrent_checks):
            if len(dev_queue) > 0:
                ready = dev_queue.popleft()
                p = multiprocessing.Process(target=main_action,
                                            args=(
                                                ready,
                                                notify_enabled,
                                                notify,
                                            ))
                p.start()
        p.join()
