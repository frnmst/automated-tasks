#!/usr/bin/env python3
#
# prepare_environment.py
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

import configparser
import sys
import shlex
import automated_tasks

class DirectoryTypeNotValid(Exception):
    """The directory type is neither of the scripts nor services type."""

def get_base_objects_directory_name(user: str, type: str, scripts_directory_name: str, services_directory_name: str):
    if type != scripts_directory_name and type != services_directory_name:
        raise DirectoryTypeNotValid
    return '/home/' + shlex.quote(user) + '/' + shlex.quote(type)

def get_base_objects_directory_name_by_user(user: str, type: str, scripts_directory_name: str, services_directory_name: str):
    return get_base_objects_directory_name(user, type, scripts_directory_name, services_directory_name) + '/by-user'

def get_objects_directory_name(top_user: str, type: str, user: str, scripts_directory_name: str, services_directory_name: str):
    return get_base_objects_directory_name_by_user(top_user, type, scripts_directory_name, services_directory_name) + '/' + shlex.quote(user)

# Read the yaml file.
def get_files_to_copy(yaml_file):
    pass

if __name__ == '__main__':
    commit = automated_tasks.get_action(shlex.quote(sys.argv[1]))

    configuration_file = shlex.quote(sys.argv[2])
    config = configparser.ConfigParser()
    config.read(configuration_file)
    running_user = config['DEFAULT']['running user']
    jobs_user = config['DEFAULT']['jobs user']
    users = config['DEFAULT']['users'].split(',')
    scripts_directory = config['DEFAULT']['scripts directory']
    services_directory = config['DEFAULT']['services directory']

    automated_tasks.check_running_user(running_user)

    # Commands.
    c = list()
    c.append(automated_tasks.gen_create_user_command(jobs_user))
    d_scripts_by_user = get_base_objects_directory_name_by_user(jobs_user, scripts_directory, scripts_directory, services_directory)
    d_services_by_user = get_base_objects_directory_name_by_user(jobs_user, services_directory, scripts_directory, services_directory)
    c.append(automated_tasks.gen_create_directory_command(d_scripts_by_user))
    c.append(automated_tasks.gen_create_directory_command(d_services_by_user))
    c.append(automated_tasks.gen_change_owners_command(d_scripts_by_user,jobs_user,jobs_user))
    c.append(automated_tasks.gen_change_owners_command(d_services_by_user,jobs_user,jobs_user))
    c.append(automated_tasks.gen_change_permissions_command(d_scripts_by_user))
    c.append(automated_tasks.gen_change_permissions_command(d_services_by_user))
    for u in users:
        c.append(automated_tasks.gen_add_users_to_group_command(u, jobs_user))
        d_scripts = get_objects_directory_name(jobs_user, scripts_directory, u, scripts_directory, services_directory)
        d_services = get_objects_directory_name(jobs_user, services_directory, u, scripts_directory, services_directory)
        c.append(automated_tasks.gen_create_directory_command(d_scripts))
        c.append(automated_tasks.gen_create_directory_command(d_services))
        c.append(automated_tasks.gen_change_owners_command(d_scripts,u,u))
        c.append(automated_tasks.gen_change_owners_command(d_services,u,u))
        c.append(automated_tasks.gen_change_permissions_command(d_scripts))
        c.append(automated_tasks.gen_change_permissions_command(d_services))

    automated_tasks.exec_or_print(commit, c)

