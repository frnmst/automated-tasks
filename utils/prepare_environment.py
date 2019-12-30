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
import yaml
import os
import pathlib

class DirectoryTypeNotValid(Exception):
    """The directory type is neither of the scripts nor services type."""

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

def print_commands(commands: list):
    for command in commands:
        assert isinstance(command, str)

    for command in commands:
        print (command)

def get_home_directory(user: str):
    return '/home/' + shlex.quote(user)

def get_base_objects_directory_name(user: str, type: str, scripts_directory_name: str, services_directory_name: str):
    if type != scripts_directory_name and type != services_directory_name:
        raise DirectoryTypeNotValid
    return get_home_directory(user) + '/' + shlex.quote(type)

def get_base_objects_directory_name_by_user(user: str, type: str, scripts_directory_name: str, services_directory_name: str):
    return get_base_objects_directory_name(user, type, scripts_directory_name, services_directory_name) + '/by-user'

def get_objects_directory_name(top_user: str, type: str, user: str, scripts_directory_name: str, services_directory_name: str):
    return get_base_objects_directory_name_by_user(top_user, type, scripts_directory_name, services_directory_name) + '/' + shlex.quote(user)

def get_files_to_copy(yaml_file: str, current_directory: str, source_files_directory: str) -> dict:
    yaml.load(yaml_file, Loader=yaml.SafeLoader)
    with open(yaml_file, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    files = dict()
    users = list()
    for argument in data:
        for script in data[argument]:
            if data[argument][script]['enabled']:
                files[script]=dict()
                files[script]['script']=dict()
                files[script]['conf']=dict()
                files[script]['service']=dict()
                files[script]['timer']=dict()

                if pathlib.Path(current_directory + '/' + source_files_directory + '/' + argument + '/' + script).is_file():
                    files[script]['script']['src'] = [current_directory + '/' + argument + '/' + script]
                    files[script]['script']['dst'] = [data[argument][script]['running user'] + '/' + script]
                else:
                    files[script]['script']['src'] = list()
                    files[script]['script']['dst'] = list()

                if 'configuration files' in data[argument][script]:
                    files[script]['conf']['src'] = [current_directory + '/' + source_files_directory + '/' + argument + '/' + e for e in data[argument][script]['configuration files']['paths']]
                    files[script]['conf']['dst'] = [data[argument][script]['running user'] + '/' + e for e in data[argument][script]['configuration files']['paths']]
                else:
                    files[script]['conf']['src'] = list()
                    files[script]['conf']['dst'] = list()

                if 'systemd unit files' in data[argument][script]:
                    files[script]['service']['src'] = [current_directory + '/' + source_files_directory + '/' + argument + '/' + e for e in data[argument][script]['systemd unit files']['paths']['service']]
                    files[script]['service']['dst'] = [data[argument][script]['running user'] + '/' + e for e in data[argument][script]['systemd unit files']['paths']['service']]
                    if 'timer' in data[argument][script]['systemd unit files']['paths']:
                        files[script]['timer']['src'] = [current_directory + '/' + source_files_directory + '/' + argument + '/' + e for e in data[argument][script]['systemd unit files']['paths']['timer']]
                        files[script]['timer']['dst'] = [data[argument][script]['running user'] + '/' + e for e in data[argument][script]['systemd unit files']['paths']['timer']]
                    else:
                        files[script]['timer']['src'] = list()
                        files[script]['timer']['dst'] = list()
                else:
                    files[script]['service']['src'] = list()
                    files[script]['service']['dst'] = list()
                    files[script]['timer']['src'] = list()
                    files[script]['timer']['dst'] = list()

                users.append(data[argument][script]['running user'])

    return files, list(set(users))

def gen_multiple_copy_file_commands_by_unit_type(files: dict, scripts_directory, services_directory):
    commands = list()

    for f in files:
        for type in files[f]:
            for s, d in zip(files[f][type]['src'], files[f][type]['dst']):
                if type == 'service' or type == 'timer':
                    commands.append(gen_copy_file_command(s, services_directory + '/' + d))
                else:
                    commands.append(gen_copy_file_command(s, scripts_directory + '/' + d))

    return commands

def extract_text_between_delimiters(file: str, start_marker: str, end_marker: str) -> str:
    """Get all the text included in two delimiters."""
    keep = False
    out = str()
    with open (file, 'r') as f:
        for line in f:
            delimiter=False
            if line.lstrip().startswith(start_marker):
                keep = True
                delimiter=True
            elif line.lstrip().startswith(end_marker):
                keep = False
                delimiter=True
            if keep and not delimiter:
                out += line
    return out

def generate_yaml_struct(input_string: str) -> str:
    """Generate a YAML string which conforms to the expected inputs for some functions of this script."""
    elements = yaml.load(input_string, Loader=yaml.BaseLoader)

    out = dict()
    for element in elements:
        type = elements[element]['type']
        if type not in out:
            out[type] = dict()
        out[type][element] = dict()
        out[type][element]['enabled'] = False
        if 'configuration files' in elements[element]:
            out[type][element]['configuration files'] = elements[element]['configuration files']
        if 'systemd unit files' in elements[element]:
            out[type][element]['systemd unit files'] = elements[element]['systemd unit files']

    return yaml.dump(out)

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    generate_yaml = False
    if len(sys.argv) > 2:
        if sys.argv[2] == '--generate-yaml':
            generate_yaml = True

    config = configparser.ConfigParser()
    config.read(configuration_file)
    jobs_user = config['DEFAULT']['jobs user']
    scripts_directory = config['DEFAULT']['scripts directory']
    services_directory = config['DEFAULT']['services directory']
    metadata_file = config['DEFAULT']['metadata file']
    deploy_script = config['DEFAULT']['deploy script']
    source_files_directory = config['DEFAULT']['source files directory']
    scripts_file = config['DEFAULT']['documentation scripts file']
    yaml_section_start_marker = config['DEFAULT']['documentation yaml section start marker']
    yaml_section_end_marker = config['DEFAULT']['documentation yaml section end marker']

    if generate_yaml:
        yaml_input = extract_text_between_delimiters(scripts_file, yaml_section_start_marker, yaml_section_end_marker)
        yaml_struct = generate_yaml_struct(yaml_input)
        print(yaml_struct, end='')
    else:
        files, users = get_files_to_copy(metadata_file, str(pathlib.Path.cwd()), source_files_directory)
        d_scripts_by_user = get_base_objects_directory_name_by_user(jobs_user, scripts_directory, scripts_directory, services_directory)
        d_services_by_user = get_base_objects_directory_name_by_user(jobs_user, services_directory, scripts_directory, services_directory)
        file_copy_commands = gen_multiple_copy_file_commands_by_unit_type(files, d_scripts_by_user, d_services_by_user)
        home_jobs = get_home_directory(jobs_user)

        c = list()

        c.append('#!/usr/bin/env bash')
        c.append('# autogenerated by automated-tasks/prepare_environment.py')
        c.append('')
        c.append('set -euo pipefail')

        c.append(gen_create_user_command(jobs_user))
        c.append(gen_create_directory_command(d_scripts_by_user))
        c.append(gen_create_directory_command(d_services_by_user))

        # Copy the deploy script before changing the permissions.
        c.append(gen_copy_file_command(deploy_script, d_services_by_user))

        c.append(gen_change_owners_command(home_jobs, jobs_user, jobs_user))
        c.append(gen_change_permissions_command(home_jobs, permissions='070'))

        # Create directories.
        # User names are gathered from the YAML file.
        for u in users:
            c.append(gen_add_users_to_group_command(u, jobs_user))
            d_scripts = get_objects_directory_name(jobs_user, scripts_directory, u, scripts_directory, services_directory)
            d_services = get_objects_directory_name(jobs_user, services_directory, u, scripts_directory, services_directory)
            c.append(gen_create_directory_command(d_scripts))
            c.append(gen_create_directory_command(d_services))

        # We need to run the copy command before chown and chmod.
        c = c + file_copy_commands

        # Change owners and permissions.
        for u in users:
            d_scripts = get_objects_directory_name(jobs_user, scripts_directory, u, scripts_directory, services_directory)
            d_services = get_objects_directory_name(jobs_user, services_directory, u, scripts_directory, services_directory)
            c.append(gen_change_owners_command(d_scripts,u,u))
            c.append(gen_change_owners_command(d_services,u,u))
            c.append(gen_change_permissions_command(d_scripts))
            c.append(gen_change_permissions_command(d_services))

        print_commands(c)
