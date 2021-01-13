#!/usr/bin/env python3
#
# qvm.py
#
# Copyright (C) 2021 Franco Masotti <franco.masotti@live.com>
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
#
#
# Original license header:
#
# qvm - Trivial management of 64 bit virtual machines with qemu.
#
# Written in 2016 by Franco Masotti/frnmst <franco.masotti@student.unife.it>
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the public
# domain worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.
r"""Run virtual machines."""

import fpyutils
import shlex
import sys


def build_remote_command(prf: dict) -> str:
    if prf['system']['display']['enabled']:
        # See https://unix.stackexchange.com/a/83812
        # See also the 'TCP FORWARDING' section in man 1 ssh.
        ssh = '-f -p ' + prf['system']['network']['ports']['host']['ssh'] + ' -L ' + prf['system']['network']['ports']['local']['vnc'] + ':127.0.0.1:' + prf['system']['network']['ports']['host']['vnc'] + ' -l ' + prf['system']['users']['host'] + ' ' + prf['system']['network']['addresses']['host']
        ssh += ' sleep 10; vncviewer 127.0.0.1::' + prf['system']['network']['ports']['local']['vnc']
    else:
        ssh = '-p ' + prf['system']['network']['ports']['guest']['ssh'] + ' -l ' + prf['system']['users']['guest'] + ' ' + prf['system']['network']['addresses']['host']

    return (
        prf['executables']['ssh']
        + ' ' + ssh
    )


def build_local_command(prf: dict) -> str:
    head = str()

    # Memory.
    memory = ' -m ' + prf['system']['memory']

    # CPU.
    cpu = ' -smp ' + prf['system']['cpu']['cores'] + ' -cpu ' + prf['system']['cpu']['type']

    # Display.
    if prf['system']['display']['enabled']:
        if prf['system']['display']['vnc']['enabled']:
            display_number = int(prf['system']['display']['vnc']['port']) - 5900
            display = '-display none -monitor pty -vnc 127.0.0.1:' + str(display_number)
        else:
            display = '-display gtk'
    else:
        display = '-display none'

    # Audio.
    if prf['system']['audio']['enabled']:
        audio = '-device ' + prf['system']['audio']['device']
        head += 'export QEMU_AUDIO_DRV=alsa;'
    else:
        audio = str()

    # Network.
    if prf['system']['network']['enabled']:
        net = '-netdev user,id=user.0'
        i = 0
        for n in prf['system']['network']['ports']:
            for j in n:
                net += ',hostfwd=tcp::' + prf['system']['network']['ports'][i][j]['host'] + '-:' + prf['system']['network']['ports'][i][j]['guest']
                i += 1
        net += ' -device e1000,netdev=user.0'
    else:
        net = str()

    # Mounts.
    if prf['system']['mount']['enabled']:
        mnt = str()
        i = 0
        for n in prf['system']['mount']['mountpoints']:
            for j in n:
                mnt += ' -virtfs local,path=' + prf['system']['mount']['mountpoints'][i][j]['path'] + ',security_model=passthrough,mount_tag=' + prf['system']['mount']['mountpoints'][i][j]['mount tag']
                i += 1
    else:
        mnt = str()

    # CD-ROM.
    if prf['system']['cdrom']['enabled']:
        cdrom = '-cdrom ' + prf['system']['cdrom']['device'] + ' -boot order=d'
    else:
        cdrom = str()

    # Mass memory.
    hdd = str()
    for drive in prf['system']['drives']:
        hdd += ' -drive file=' + drive

    return (
        head
        + ' ' + prf['executables']['qemu']
        + ' ' + prf['options']
        + ' ' + memory
        + ' ' + cpu
        + ' ' + display
        + ' ' + net
        + ' ' + cdrom
        + ' ' + audio
        + ' ' + mnt
        + ' ' + hdd
    )


if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)
    type = shlex.quote(sys.argv[2])
    profile = shlex.quote(sys.argv[3])

    prf = config[type][profile]
    if prf['enabled']:
        if type == 'local':
            command = build_local_command(prf)
        elif type == 'remote':
            command = build_remote_command(prf)

    fpyutils.shell.execute_command_live_output(command, dry_run=False)
