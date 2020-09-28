#!/usr/bin/env python3
#
# prepare_environment.py
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

import configparser
import sys
import shlex
import yaml
import pathlib


class DirectoryTypeNotValid(Exception):
    """The directory type is neither of the scripts nor services type."""


def gen_create_user_command(user: str) -> str:
    return 'useradd -m -s /bin/bash -U ' + shlex.quote(user)


def gen_add_users_to_group_command(user: str, group: str) -> str:
    return 'usermod -aG ' + shlex.quote(group) + ' ' + shlex.quote(user)


def gen_create_directory_command(directory: str) -> str:
    return 'mkdir -p ' + shlex.quote(directory)


def gen_change_owners_command(file: str, owner_user: str,
                              owner_group: str) -> str:
    return 'chown -R ' + shlex.quote(owner_user) + ':' + shlex.quote(
        owner_group) + ' ' + file


def gen_change_permissions_command(file: str, permissions: str = '700') -> str:
    return 'chmod -R ' + shlex.quote(permissions) + ' ' + file


def gen_copy_file_command(src: str, dst: str) -> str:
    return 'cp -aR ' + shlex.quote(src) + ' ' + shlex.quote(dst)


def print_commands(commands: list):
    for command in commands:
        if not isinstance(command, str):
            raise TypeError

    for command in commands:
        print(command)


def get_home_directory(user: str) -> str:
    return '/home/' + shlex.quote(user)


def get_base_objects_directory_name(user: str, type: str,
                                    scripts_directory_name: str,
                                    services_directory_name: str) -> str:
    if type != scripts_directory_name and type != services_directory_name:
        raise DirectoryTypeNotValid
    return get_home_directory(user) + '/' + shlex.quote(type)


def get_base_objects_directory_name_by_user(
        user: str, type: str, scripts_directory_name: str,
        services_directory_name: str) -> str:
    return get_base_objects_directory_name(
        user, type, scripts_directory_name,
        services_directory_name) + '/by-user'


def get_objects_directory_name(top_user: str, type: str, user: str,
                               scripts_directory_name: str,
                               services_directory_name: str) -> str:
    return get_base_objects_directory_name_by_user(
        top_user, type, scripts_directory_name,
        services_directory_name) + '/' + shlex.quote(user)


def get_files_to_copy(yaml_file: str, current_directory: str,
                      source_files_directory: str) -> tuple:
    r"""Get a list of source and destination file paths as well as the running users."""
    with open(yaml_file, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    files = dict()
    users = list()
    for argument in data:
        for script in data[argument]:
            if data[argument][script]['enabled']:

                # Separate the files by type.
                files[script] = dict()
                files[script]['script'] = dict()
                files[script]['conf'] = dict()
                files[script]['service'] = dict()
                files[script]['timer'] = dict()

                # Copy the main script.
                if pathlib.Path(current_directory + '/' +
                                source_files_directory + '/' + argument + '/' +
                                script).is_file():
                    files[script]['script']['src'] = [
                        current_directory + '/' + source_files_directory +
                        '/' + argument + '/' + script
                    ]
                    files[script]['script']['dst'] = [
                        data[argument][script]['running user'] + '/' + script
                    ]
                else:
                    files[script]['script']['src'] = list()
                    files[script]['script']['dst'] = list()

                if 'configuration files' in data[argument][script]:
                    files[script]['conf']['src'] = [
                        current_directory + '/' + source_files_directory +
                        '/' + argument + '/' + e for e in data[argument]
                        [script]['configuration files']['paths']
                    ]
                    files[script]['conf']['dst'] = [
                        data[argument][script]['running user'] + '/' + e
                        for e in data[argument][script]['configuration files']
                        ['paths']
                    ]
                else:
                    files[script]['conf']['src'] = list()
                    files[script]['conf']['dst'] = list()

                if 'systemd unit files' in data[argument][script]:
                    files[script]['service']['src'] = [
                        current_directory + '/' + source_files_directory +
                        '/' + argument + '/' + e for e in data[argument]
                        [script]['systemd unit files']['paths']['service']
                    ]
                    files[script]['service']['dst'] = [
                        data[argument][script]['running user'] + '/' + e
                        for e in data[argument][script]['systemd unit files']
                        ['paths']['service']
                    ]

                    # Timer unit files are not required.
                    if 'timer' in data[argument][script]['systemd unit files'][
                            'paths']:
                        files[script]['timer']['src'] = [
                            current_directory + '/' + source_files_directory +
                            '/' + argument + '/' + e for e in data[argument]
                            [script]['systemd unit files']['paths']['timer']
                        ]
                        files[script]['timer']['dst'] = [
                            data[argument][script]['running user'] + '/' + e
                            for e in data[argument][script]
                            ['systemd unit files']['paths']['timer']
                        ]
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


def gen_multiple_copy_file_commands_by_file_type(files: dict,
                                                 scripts_directory,
                                                 services_directory) -> list:
    r"""Generate commands to copy the files in the appropriate directories.

    .. note:: We need to iterate by type to select
        the correct destination directory.
    """
    commands = list()

    for f in files:
        for type in files[f]:
            for s, d in zip(files[f][type]['src'], files[f][type]['dst']):
                if type == 'service' or type == 'timer':
                    commands.append(
                        gen_copy_file_command(s, services_directory + '/' + d))
                elif type == 'script' or type == 'conf':
                    commands.append(
                        gen_copy_file_command(s, scripts_directory + '/' + d))

    return commands


def extract_text_between_delimiters(file: str, start_marker: str,
                                    end_marker: str) -> str:
    r"""Get all the text included between two delimiters."""
    keep = False
    out = str()
    with open(file, 'r') as f:
        for line in f:
            delimiter = False
            if line.lstrip().startswith(start_marker):
                keep = True
                delimiter = True
            elif line.lstrip().startswith(end_marker):
                keep = False
                delimiter = True
            if keep and not delimiter:
                out += line
    return out


def generate_yaml_struct(input_string: str) -> str:
    r"""Generate a YAML string.

    .. note:: The string returned by this function conforms
        to the expected inputs for other functions of this script.
    """
    elements = yaml.load(input_string, Loader=yaml.BaseLoader)

    out = dict()
    for element in elements:
        category = elements[element]['category']
        if category not in out:
            out[category] = dict()
        out[category][element] = dict()
        out[category][element]['enabled'] = False
        out[category][element]['running user'] = elements[element][
            'running user']
        if 'configuration files' in elements[element]:
            out[category][element]['configuration files'] = elements[element][
                'configuration files']
        if 'systemd unit files' in elements[element]:
            out[category][element]['systemd unit files'] = elements[element][
                'systemd unit files']

    return yaml.dump(out)


def set_script_headers() -> list:
    commands = list()
    commands.append('#!/usr/bin/env bash')
    commands.append('#')
    commands.append('# GPLv3+ license')
    commands.append('# (C) 2019-2020 Franco Masotti <franco.masotti@live.com>')
    commands.append('#')
    commands.append(
        '# autogenerated by automated-tasks/prepare_environment.py')
    commands.append('')
    commands.append('set -euo pipefail')

    return commands


if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    generate_yaml = False
    if len(sys.argv) > 2:
        if sys.argv[2] == '--generate-yaml' or sys.argv[
                2] == '--generate-metadata':
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
    yaml_section_start_marker = config['DEFAULT'][
        'documentation yaml section start marker']
    yaml_section_end_marker = config['DEFAULT'][
        'documentation yaml section end marker']

    if generate_yaml:
        yaml_input = extract_text_between_delimiters(
            scripts_file, yaml_section_start_marker, yaml_section_end_marker)
        yaml_struct = generate_yaml_struct(yaml_input)
        print(yaml_struct, end='')
    else:
        files, users = get_files_to_copy(metadata_file,
                                         str(pathlib.Path.cwd()),
                                         source_files_directory)
        directory_scripts_by_user = get_base_objects_directory_name_by_user(
            jobs_user, scripts_directory, scripts_directory,
            services_directory)
        directory_services_by_user = get_base_objects_directory_name_by_user(
            jobs_user, services_directory, scripts_directory,
            services_directory)
        file_copy_commands = gen_multiple_copy_file_commands_by_file_type(
            files, directory_scripts_by_user, directory_services_by_user)
        home_jobs = get_home_directory(jobs_user)

        c = set_script_headers()

        c.append(gen_create_user_command(jobs_user))
        c.append(gen_create_directory_command(directory_scripts_by_user))
        c.append(gen_create_directory_command(directory_services_by_user))

        # Copy the deploy script before changing the permissions.
        c.append(
            gen_copy_file_command(deploy_script, directory_services_by_user))

        c.append(gen_change_owners_command(home_jobs, jobs_user, jobs_user))
        c.append(gen_change_permissions_command(home_jobs, permissions='070'))

        # Create directories.
        # User names are gathered from the YAML file.
        for u in users:
            c.append(gen_add_users_to_group_command(u, jobs_user))
            directory_scripts = get_objects_directory_name(
                jobs_user, scripts_directory, u, scripts_directory,
                services_directory)
            directory_services = get_objects_directory_name(
                jobs_user, services_directory, u, scripts_directory,
                services_directory)
            c.append(gen_create_directory_command(directory_scripts))
            c.append(gen_create_directory_command(directory_services))

        # We need to run the copy command before chown and chmod.
        c = c + file_copy_commands

        # Change owners and permissions.
        for u in users:
            directory_scripts = get_objects_directory_name(
                jobs_user, scripts_directory, u, scripts_directory,
                services_directory)
            directory_services = get_objects_directory_name(
                jobs_user, services_directory, u, scripts_directory,
                services_directory)
            c.append(gen_change_owners_command(directory_scripts, u, u))
            c.append(gen_change_owners_command(directory_services, u, u))
            c.append(gen_change_permissions_command(directory_scripts))
            c.append(gen_change_permissions_command(directory_services))

        print_commands(c)
