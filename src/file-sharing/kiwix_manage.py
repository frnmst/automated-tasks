#!/usr/bin/env python3
#
# kiwix_manage.py
#
# Copyright (C) 2020 Franco Masotti <franco.masotti@live.com>
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

########
# Main #
########

import bs4
import datetime
import pathlib
import re
import requests
import sys
import shlex
import shutil
import subprocess
import urllib.parse
import yaml

def separate_pattern_from_string(string: str, pattern: str) -> tuple:
    r"""Separate a pattern from a string."""
    string_without_pattern = remove_component(string, pattern)
    component = find_component(string, pattern)

    return string_without_pattern, component

def separate_pattern_from_strings(strings: list, pattern: str) -> dict:
    r"""Separate a batch of strings from their patterns."""
    for string in strings:
        assert isinstance(string, str)

    elements = dict()
    # Populate the date elements.
    for string in strings:
        common, component = separate_pattern_from_string(string, pattern)
        if common not in elements:
            # Build an empty list of length corresponding
            # to the number of entries without the date component in the file name.
            elements[common] = list()
        elements[common].append(component)

    return elements

def filter_max_elements_in_dict_nested_lists(elements: dict) -> dict:
    r"""Given a dictionary with lists, find the maxium elements of each list and remove the other elements."""
    # Get the most recent dates by group and rebuild the URLs.
    filtered_elements = dict()
    for element in elements:
        filtered_elements[element] = max(elements[element])

    return filtered_elements

def get_most_recent_elements(uris: list, date_regex_pattern: str, date_format_string: str) -> dict:
    r"""Filter elements by date and return the most recent ones."""
    for uri in uris:
        assert isinstance(uri, str)

    elements = separate_pattern_from_strings(uris, date_regex_pattern)
    # Transform the date strings to datetime objects.
    for element in elements:
        i = 0
        while i<len(elements[element]):
            elements[element][i] = str_to_datetime(elements[element][i], date_format_string)
            i += 1
    return filter_max_elements_in_dict_nested_lists(elements)

def filter_uris_by_pattern(uris: list, pattern: str):
    r"""Filter URIs by regex pattern."""
    filtered_uris = list()
    for uri in uris:
        if find_component(uri, pattern) is not None:
            filtered_uris.append(uri)

    return filtered_uris

def compare_uris(local_uris: dict, remote_uris: dict) -> tuple:
    r"""Given two sets of URIs select the actions to do with the elements each one by placing them into two new sets."""
    files_to_download = list()
    files_to_delete = list()
    for remote in remote_uris:
        exists_locally = False
        for local in local_uris:
            if remote == local:
                exists_locally = True
                # Get the element in the local files list corresponding to the current remote file.
                # Only download fresh files.
                if local_uris[local] < remote_uris[remote]:
                   files_to_download.append(rebuild_uri_with_date(remote, remote_uris[remote], '%Y-%m'))
                   files_to_delete.append(rebuild_uri_with_date(local, local_uris[local], '%Y-%m'))
        if not exists_locally:
            files_to_download.append(rebuild_uri_with_date(remote, remote_uris[remote], '%Y-%m'))

    return files_to_download, files_to_delete

def download_files(files_to_download: list, downloader: str, downloader_args: str, root_url: str, file_directory: str):
    r"""Download a batch of files."""
    delete_temporary_directory = False
    for i, download in enumerate(files_to_download):
        full_remote_uri = rebuild_uri(root_url, download)
        full_local_uri = rebuild_uri(file_directory, download)
        if i == len(files_to_download) - 1:
            delete_temporary_directory = True
        download_binary_file(full_remote_uri, full_local_uri, downloader, downloader_args, delete_temporary_directory)

def delete_files(files_to_delete: list, file_directory: str):
    r"""Delete a batch of files."""
    for delete in files_to_delete:
        full_local_uri = rebuild_uri(file_directory, delete)
        delete_file(full_local_uri)


#########
# Utils #
#########

def get_relative_path(path: str) -> str:
    r"""Get the last component of a path."""
    return str(pathlib.Path(path).name)

def get_relative_paths(paths: list) -> list:
    r"""Get the last components of a list of paths."""
    relative = list()
    for path in paths:
        relative.append(get_relative_path(path))

    return relative

def get_last_path_component_from_url(url: str) -> str:
    r"""Transform a string to a datetime object."""
    component = urllib.parse.urlsplit(url).path
    return get_relative_path(component)

def remove_component(element: str, pattern: str) -> str:
    r"""Remove the date component from the name."""
    return re.split(pattern, element)[0]

def find_component(element: str, pattern: str) -> str:
    r"""Return the date component from the name."""
    f = re.findall(pattern, element)
    if len(f) == 1:
        return f[0]
    else:
        return None

def str_to_datetime(date: str, date_formatting_string: str) -> datetime.datetime:
    r"""Transform a string into a datetime object."""
    return datetime.datetime.strptime(date, date_formatting_string)

def datetime_to_str(date: datetime.datetime, date_formatting_string: str) -> str:
    r"""Transform a datetime object into a string."""
    return datetime.datetime.strftime(date, date_formatting_string)

def rebuild_uri(uri_base: str, path: str) -> str:
    """Rebuild a URI by a trailing forward slash if necessary and a path.
    ..note: see https://stackoverflow.com/a/59818095
    """
    uri_base = uri_base if uri_base.endswith('/') else f"{uri_base}/"
    return uri_base + path

def rebuild_uri_with_date(uri_base: str, date: datetime, date_formatting_string: str, extension: str = '.zim') -> str:
    r"""Rebuild the original URI which has been stripped from the date and file extension components."""
    return uri_base + datetime_to_str(date, date_formatting_string) + extension

def get_a_href_elements_from_url(url: str) -> list:
    r"""Given a url, download the file and, if it is an HTML file, find all "a href" elements."""
    soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
    # Get the content of the HTML tag.
    return [link.get('href') for link in soup.find_all('a')]

def execute_command_live_output(command: str) -> int:
    r"""Execute and print the output of a command relatime."""
    # See https://stackoverflow.com/a/53811881
    #
    # Copyright (C) 2018 Tom Hale @ Stack Exchange (https://stackoverflow.com/a/53811881)
    # Copyright (C) 2020 Franco Masotti <franco.masotti@live.com>
    #
    # This script is licensed under a
    # Creative Commons Attribution-ShareAlike 4.0 International License.
    #
    # You should have received a copy of the license along with this
    # work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
    process = subprocess.Popen(command,shell=True,stderr=subprocess.PIPE)

    go = True
    while go:
        out = process.stderr.readline().decode('UTF-8')
        if out == str() and process.poll() is not None:
            go = False
        if go and out != str():
            sys.stdout.write(out)
            sys.stdout.flush()

    return process.returncode

def download_binary_file_requests(url: str, destination: str):
    r"""Download a binary file with Python Requests."""
    # See https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests/39217788#39217788
    #
    # Copyright (C) 2016 John Zwinck @ Stack Exchange (https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests/39217788#39217788)
    # Copyright (C) 2020 Martijn Pieters @ Stack Exchange (https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests/39217788#39217788)
    # Copyright (C) 2020 Franco Masotti <franco.masotti@live.com>
    #
    # This script is licensed under a
    # Creative Commons Attribution-ShareAlike 4.0 International License.
    #
    # You should have received a copy of the license along with this
    # work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.

    with requests.get(url, stream=True) as r:
        with open(destination, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def download_binary_file_aria2c(downloader_args: str, parent_directory: str, url: str, destination: str, temporary_directory: str = 'tmp', delete_temporary_directory: bool = False):
    r"""Download a binary file with aria2."""
    p = shlex.quote(parent_directory)
    d = shlex.quote(destination)
    u = shlex.quote(url)
    # Get the relative path.
    t = str(pathlib.Path(shlex.quote(temporary_directory)).name)
    pt = str(pathlib.Path(p, t))
    ptd = str(pathlib.Path(pt, d))

    # Save the file to a temporary file so that if the download is interrupted
    # the pipeline does not detect that the file exists.
    command = 'aria2c ' + downloader_args + ' --dir=' + pt + ' --out=' + d + ' ' + u
    try:
        return_code = execute_command_live_output(command)
        if return_code == 0:
            try:
                shutil.move(ptd, p)
                if delete_temporary_directory:
                    try:
                        # See https://docs.python.org/3/library/shutil.html?highlight=shutil#shutil.rmtree.avoids_symlink_attacks
                        if shutil.rmtree.avoids_symlink_attacks:
                            shutil.rmtree(pt)
                        else:
                            raise shutil.Error
                    except shutil.Error as e:
                        print (e)
            except shutil.Error as e:
                print (e)
        else:
            sys.exit(1)
    except subprocess.SubprocessError as e:
        print (e)
        raise e
        sys.exit(1)

def get_parent_directory_name(path: str) -> str:
    r"""Get parent directory name."""
    return str(pathlib.Path(path).parent)

def pre_download_hooks(destination: str, permissions: int = 0o700):
    r"""Run selected actions before downloading the files."""
    pathlib.Path(destination).parent.mkdir(mode=permissions,parents=True,exist_ok=True)

def post_download_hooks(path: str, permissions: str):
    r"""Run selected actions after downloading the files."""
    # Change file permissions.
    pathlib.Path(path).chmod(permissions)

def download_binary_file(url: str,
                         destination: str,
                         downloader: str = 'requests',
                         downloader_args: str = str(),
                         permissions: int = 0o700,
                         delete_temporary_directory: bool = False):
    r"""Download a binary file."""
    assert downloader in ['requests', 'aria2c']

    print ('Downloading ' + url + ' as ' + destination)
    pre_download_hooks(destination, permissions)
    if downloader == 'requests':
        download_binary_file_requests(url, destination)
    elif downloader == 'aria2c':
        download_binary_file_aria2c(downloader_args, get_parent_directory_name(destination), url, get_relative_path(destination), 'tmp', delete_temporary_directory)
    post_download_hooks(destination, permissions)

def delete_file(file: str):
    r"""Delete a file."""
    print ('Deleting ' + file)
    pathlib.Path(file).unlink()

def list_directory_files(directory: str) -> list:
    r"""Get a list of files in a directory"""
    files = list()
    p = pathlib.Path(directory)
    if p.is_dir():
        for child in p.iterdir():
            if child.is_file():
                files.append(str(child))

    return files

def run_kiwix_server(url_root_location: str, threads: int, port: int, directory: str):
    r"""Serve the ZIM files."""
    command = 'kiwix-serve --verbose --urlRootLocation ' + shlex.quote(url_root_location) + ' --threads ' + shlex.quote(str(threads)) + ' --port ' + shlex.quote(str(port)) + ' ' + shlex.quote(directory) + '/*.zim'
    execute_command_live_output(command)

def pipeline():
    # Load the configuration.
    configuration_file = shlex.quote(sys.argv[1])
    action = shlex.quote(sys.argv[2])
    with open(configuration_file, 'r') as f:
        configuration = yaml.load(f, Loader=yaml.SafeLoader)
    dry_run = configuration['dry run']
    serve = configuration['serve']
    downloads = configuration['downloads']

    if action == '--serve':
        run_kiwix_server(serve['url root location'], serve['threads'], serve['port'], serve['directory'])
    elif action == '--download':
        for section in downloads:
            root_url = rebuild_uri(downloads[section]['root url'], str())

            remote_uris = get_a_href_elements_from_url(root_url)
            remote_uris = filter_uris_by_pattern(remote_uris, downloads[section]['regex patterns']['files to download'])
            remote_uris = filter_uris_by_pattern(remote_uris, downloads[section]['regex patterns']['date'])
            remote_uris = get_relative_paths(remote_uris)

            most_recent_remote_uris = get_most_recent_elements(remote_uris,downloads[section]['regex patterns']['date'],downloads[section]['date transformation string'])

            local_uris = list_directory_files(downloads[section]['download directory'])
            local_uris = filter_uris_by_pattern(local_uris, downloads[section]['regex patterns']['date'])
            local_uris = get_relative_paths(local_uris)

            most_recent_local_uris = get_most_recent_elements(local_uris,downloads[section]['regex patterns']['date'],downloads[section]['date transformation string'])

            files_to_download, files_to_delete = compare_uris(most_recent_local_uris, most_recent_remote_uris)

            download_files(files_to_download, downloads[section]['downloader']['name'], downloads[section]['downloader']['args'], root_url, downloads[section]['download directory'])
            delete_files(files_to_delete, downloads[section]['download directory'])

if __name__ == '__main__':
    pipeline()
