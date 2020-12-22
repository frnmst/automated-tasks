#!/usr/bin/env python3
#
# extract_gpx_data_from_dashcams.py
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
r"""Generate GPX files from embedded EXIF metadata in videos."""

import filecmp
import fpyutils
import sys
import shlex
import pathlib
import datetime
import multiprocessing
import re


def filter_files(dir: str, regex: str, older_than_days: int) -> list:
    r"""Iterate recursively to find files matching the regex."""
    regex = re.compile(regex)
    files_to_process = list()
    for f in pathlib.Path(dir).rglob('*'):
        if f.is_file() and regex.match(f.name) and (
                datetime.date.today() - datetime.date.fromtimestamp(
                    f.stat().st_mtime)).days > older_than_days:
            files_to_process.append(str(f))

    return files_to_process


def process(exiftool_binary: str, file: pathlib.Path, gpx_template_file: str,
            remove_processed_file: bool, remove_corrupt_file: bool) -> list:
    r"""Extract the metadata from the video files."""
    processed_gpx_file = None
    corrupt_video_file = None
    removed_video_file = None

    print('Processing ' + str(file) + '...')
    command = exiftool_binary + ' -extractEmbedded ' + str(file)
    if fpyutils.shell.execute_command_live_output(command) == 0:
        command = exiftool_binary + ' -extractEmbedded -printFormat ' + shlex.quote(
            gpx_template_file) + ' ' + str(file) + ' > ' + str(file) + '.gpx'
        fpyutils.shell.execute_command_live_output(command)
        processed_gpx_file = str(file) + '.gpx'
        print('OK')
        if remove_processed_file:
            file.unlink()
            removed_video_file = str(file)
    else:
        corrupt_video_file = str(file)
        if remove_corrupt_file:
            file.unlink()
            removed_video_file = str(file)
        print('KO')

    return [
        str(file), processed_gpx_file, corrupt_video_file, removed_video_file
    ]


#############
# Callbacks #
#############
process_results = dict()
process_errors = list()


def collect_process_result(p):
    r"""Success for get_copy_list."""
    global process_results
    process_results[p[0]] = [p[1], p[2], p[3]]


def collect_process_error(p):
    r"""Error for get_copy_list."""
    global process_errors
    print(p)


if __name__ == '__main__':
    configuration_file = shlex.quote(shlex.quote(sys.argv[1]))
    config = fpyutils.yaml.load_configuration(configuration_file)

    processed_gpx_files = list()
    removed_video_files = list()
    corrupt_video_files = list()
    removed_duplicate_gpx_files = list()

    files_to_process = filter_files(
        config['files']['root dir'], config['files']['regex'],
        config['files']['process files older than days'])

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for f in files_to_process:
        pool.apply_async(func=process,
                         args=(config['binaries']['exiftool'], pathlib.Path(f), config['files']['gpx template file'],
                               config['remove']['processed files'],
                               config['remove']['corrupt files']),
                         callback=collect_process_result,
                         error_callback=collect_process_error)
    pool.close()
    pool.join()

    # Sort data.
    for e in process_results:
        if process_results[e][0] is not None:
            processed_gpx_files.append(process_results[e][0])
        if process_results[e][1] is not None:
            corrupt_video_files.append(process_results[e][1])
        if process_results[e][2] is not None:
            removed_video_files.append(process_results[e][2])

    pgf = len(processed_gpx_files)
    if config['remove']['duplicate gpx files'] and pgf > 0:
        i = 0
        go = True
        keep = list()
        j = len(processed_gpx_files)
        while go:
            alpha = processed_gpx_files.pop(i)
            keep.append(alpha)

            g2 = True
            if len(processed_gpx_files) == 0:
                g2 = False

            j = 0
            while g2:
                if filecmp.cmp(alpha, processed_gpx_files[j]):
                    to_delete = processed_gpx_files.pop(j)
                    pathlib.Path(to_delete).unlink()
                    removed_duplicate_gpx_files.append(to_delete)
                else:
                    j += 1

                if j == len(processed_gpx_files):
                    g2 = False

            if i == len(processed_gpx_files):
                go = False

    message = ('processed gpx files: ' + str(pgf) + '\n' +
               'removed video files: ' + str(len(removed_video_files)) + '\n' +
               'corrupt video files: ' + str(len(corrupt_video_files)) + '\n' +
               'removed duplicate gpx files :' +
               str(len(removed_duplicate_gpx_files)) + '\n')

    if config['notify']['gotify']['enabled']:
        m = config['notify']['gotify']['message'] + '\n' + message
        fpyutils.notify.send_gotify_message(
            config['notify']['gotify']['url'],
            config['notify']['gotify']['token'], m,
            config['notify']['gotify']['title'],
            config['notify']['gotify']['priority'])
    if config['notify']['email']['enabled']:
        fpyutils.notify.send_email(message,
                                   config['notify']['email']['smtp server'],
                                   config['notify']['email']['port'],
                                   config['notify']['email']['sender'],
                                   config['notify']['email']['user'],
                                   config['notify']['email']['password'],
                                   config['notify']['email']['receiver'],
                                   config['notify']['email']['subject'])
