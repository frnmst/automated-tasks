#!/usr/bin/env python3
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

import shlex
import subprocess
import os
import pwd

# Exceptions.
class RunningUserNotMatches(Exception):
    """The user running the script is not the one expected."""

class UnknownCLIOption(Exception):
    """Unknown CLI option."""

# Gen commands.
def gen_create_user_command(user: str) -> str:
    return 'useradd -m -s /bin/bash -U ' + shlex.quote(user)

def gen_add_users_to_group_command(user: str, group: str):
    return 'usermod -aG ' + shlex.quote(group) + ' ' + shlex.quote(user)

def gen_create_directory_command(directory: str):
    return 'mkdir -p ' + shlex.quote(directory)

def gen_change_owners_command(file: str, owner_user: str, owner_group: str):
    return 'chown -R ' + shlex.quote(owner_user) + ':' + shlex.quote(owner_group) + ' ' + file

def gen_change_permissions_command(file: str, permissions: str='700'):
    return 'chmod -R ' + shlex.quote(permissions) + ' ' + file

def gen_copy_file_command(src: str, dst: str):
    return 'cp -aR ' + shlex.quote(src) + ' ' + shlex.quote(dst)

def gen_write_to_file_command(content: str, file: str):
    return 'echo ' + shlex.quote(content) + ' > ' + shlex.quote(file)

def gen_read_from_file_command(file: str):
    return 'cat ' + shlex.quote(file)

# Commit.
def commit_commands(commands: list):
    """

    .. note: all commands must have a retcode of 0 otherwise a subprocess exception is raised.
    """
    for command in commands:
        assert isinstance(command, str)

    print ('committing...')
    out = list()
    for command in commands:
        # capture output and return code.
        #out.append(subprocess.run(command), capture_output=True, check=True, timeout=30))
        pass

def print_commands(commands: list):
    for command in commands:
        assert isinstance(command, str)

    for command in commands:
        print (command)

# CLI.
def get_action(action: str) -> bool:
    if action == 'commit':
        return True
    elif action == 'no-commit':
        return False
    else:
        raise UnknownCLIOption

def check_running_user(expected_username: str):
    if pwd.getpwuid(os.getuid()).pw_name != expected_username:
        raise RunningUserNotMatches

def exec_or_print(commit, commands):
    if commit:
        commit_commands(commands)
    else:
        print_commands(commands)
