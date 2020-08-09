#!/usr/bin/env python3
#
# archive_media_files.py
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php?title=Udisks&oldid=575618
# Copyright (C)  2019-2020  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".
#
# Note: this program was inspired by:
# 1. https://github.com/frnmst/automated-tasks/blob/master/archiving/archive_documents_simple.sh
# 2. https://frnmst.gitlab.io/notes/automatic-removable-media-synchronization.html
# 3. the archive_media_files.sh script previusly present in this repository
# all released under the GFDLv1.3+
r"""Archive media files."""

import fpyutils
import pathlib
import re
import subprocess
import shlex
import json
import datetime
import multiprocessing
import pyudev
import shutil
import sys


def find_media_files(dir: str, regex: str) -> list:
    r"""Iterate recursively to find files matching the regex."""
    regex = re.compile(regex)
    files_to_copy = list()
    for f in pathlib.Path(dir).rglob('*'):
        if f.is_file() and regex.match(f.name):
            files_to_copy.append(str(f))

    return files_to_copy


def get_date_value(file: str, exiftool_binary: str = '/usr/bin/vendor_perl/exiftool', date_format: str = '%F %T %z') -> str:
    r"""Given a file compute the datetime path components based on its metadata."""
    command = exiftool_binary + ' -tab -dateformat \"' + date_format + '\" -json ' + file
    s = subprocess.run(shlex.split(command), capture_output=True)
    out = s.stdout.decode('UTF-8')
    j = json.loads(out)
    jj = j[0]
    # 0. use EXIF data DateTimeOriginal.
    if 'DateTimeOriginal' in jj:
        date_value = jj['DateTimeOriginal']['val']
    # 1. use EXIF data MediaCreateDate.
    elif 'MediaCreateDate' in jj:
        date_value = jj['MediaCreateDate']['val']
    # 2. use EXIF CreateDate.
    elif 'CreateDate' in jj:
        date_value = jj['CreateDate']['val']
    # 3. use last modification time
    elif 'FileModifyDate' in jj:
        date_value = jj['FileModifyDate']['val']
    # 4. use time of last status change
    elif 'FileInodeChangeDate' in jj:
        date_value = jj['FileInodeChangeDate']['val']
    # 5. use last access time
    elif 'FileAccessDate' in jj:
        date_value = jj['FileAccessDate']['val']
    # 6. use the current date.
    else:
        # https://stackoverflow.com/questions/2720319/python-figure-out-local-timezone#comment90123949_39079819
        s = datetime.datetime.now().astimezone().tzinfo
        t = datetime.datetime.now(tz=s)
        date_value = t.strftime(date_format)

    print(out)

    return date_value


def get_path_from_date_value(date_value: str,
                             date_format: str = '%Y-%m-%d %H:%M:%S %z') -> str:
    r"""Get a relative path using dates."""
    d = datetime.datetime.strptime(date_value, date_format)
    # Pad 1-digit months with 1 zeros.
    return str(pathlib.Path(str(d.year), str(d.month).zfill(2)))


def rsync(src: str,
          base_dst: str,
          dst: str,
          static_options: str,
          perm_map: dict,
          remove_source_files: str = False) -> str:
    r"""Archive the files."""
    options = str()
    if remove_source_files:
        options += static_options + ' --remove-source-files'
    options += '--owner --group '
    options += '--chown=' + str(perm_map['uid']) + ':' + str(
        perm_map['gid']) + ' '
    options += '--chmod=D' + str(perm_map['dir']) + ',F' + str(
        perm_map['file']) + ' '
    options = static_options + ' ' + options

    pathlib.Path(shlex.quote(dst)).parent.mkdir(mode=0o700,
                                                parents=True,
                                                exist_ok=True)

    # Recursively change owner for the directories.
    # Do one more round because our directory structure is is /a/b/c/base/uuid
    # with base/uuid being base_dst.
    p = pathlib.Path(shlex.quote(dst)).parent
    while str(p) != str(pathlib.Path(base_dst).parent.parent):
        shutil.chown(str(p),
                     user=perm_map['uid'],
                     group=perm_map['gid'])
        # https://stackoverflow.com/a/60052847
        perms = int(str(perm_map['dir']), base=8)
        p.chmod(perms)
        p = p.parent

    command = 'rsync ' + options + ' ' + shlex.quote(src) + ' ' + shlex.quote(
        dst)
    print(command)
    fpyutils.shell.execute_command_live_output(command, dry_run=False)

    return src


def get_copy_list(file: str, dst_dir: str, exiftool_binary: str = '/usr/bin/vendor_perl/exiftool') -> list:
    r"""Iterate recursively to find files matching the regex."""
    date_value = get_date_value(file, exiftool_binary)
    relative_dst_dir = get_path_from_date_value(date_value)
    full_dst_dir = pathlib.Path(dst_dir, relative_dst_dir)

    return [file, str(pathlib.Path(full_dst_dir, pathlib.Path(file).name))]


#############
# Callbacks #
#############
rsync_results = list()
rsync_errors = list()
get_copy_list_results = dict()
get_copy_list_errors = dict()


def collect_rsync_result(result):
    r"""Success for rsync."""
    global rsync_results
    rsync_results.append(result)


def collect_rsync_error(result):
    r"""Error for rsync."""
    global rsync_errors
    rsync_errors.append(result)


def collect_get_copy_list_result(cl):
    r"""Success for get_copy_list."""
    global get_copy_list_results
    get_copy_list_results[cl[0]] = cl[1]


def collect_get_copy_list_error(result):
    r"""Error for get_copy_list."""
    global get_copy_list_errors
    print(result)

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)

    print('waiting for these uuids: ' + str(config['devices']['uuids']))

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('block')

    for device in iter(monitor.poll, None):
        if device.action == 'add' and 'ID_FS_UUID' in device and device.get(
                'ID_FS_UUID') in config['devices']['uuids']:
            uuid = device.get('ID_FS_UUID')

            fpyutils.shell.execute_command_live_output(
                'mount /dev/disk/by-uuid/' + uuid + ' ' +
                config['files']['rsync']['src dir'])

            files = find_media_files(config['files']['rsync']['src dir'],
                                     config['files']['regex'])

            dst_dir = str(
                pathlib.Path(shlex.quote(config['files']['rsync']['dst dir']),
                             uuid))
            pool = multiprocessing.Pool(multiprocessing.cpu_count())
            for f in files:
                pool.apply_async(func=get_copy_list,
                                 args=(f, dst_dir, shlex.quote(config['binaries']['exiftool'])),
                                 callback=collect_get_copy_list_result,
                                 error_callback=collect_get_copy_list_error)
            pool.close()
            pool.join()

            pool = multiprocessing.Pool(multiprocessing.cpu_count())
            for e in get_copy_list_results:
                pool.apply_async(
                    func=rsync,
                    args=(e, dst_dir, get_copy_list_results[e],
                          config['files']['rsync']['options'],
                          config['files']['rsync']['permission maps'],
                          config['files']['rsync']['remove source files']),
                    callback=collect_rsync_result,
                    error_callback=collect_rsync_error)
            pool.close()
            pool.join()

            rsync_successful_transfers = len(rsync_results)
            rsync_failed_transfers = len(rsync_errors)

            fpyutils.shell.execute_command_live_output('sync')
            fpyutils.shell.execute_command_live_output(
                'umount ' + config['files']['rsync']['src dir'])

            message = 'uuid: ' + uuid + '\n' + 'successfull: ' + str(
                rsync_successful_transfers) + '\n' + 'failed: ' + str(
                    rsync_failed_transfers)
            print(message)
            if config['notify']['gotify']['enabled']:
                m = config['notify']['gotify']['message'] + '\n' + message
                fpyutils.notify.send_gotify_message(
                    config['notify']['gotify']['url'],
                    config['notify']['gotify']['token'], m,
                    config['notify']['gotify']['title'],
                    config['notify']['gotify']['priority'])
            if config['notify']['email']['enabled']:
                fpyutils.notify.send_email(
                    message, config['notify']['email']['smtp server'],
                    config['notify']['email']['port'],
                    config['notify']['email']['sender'],
                    config['notify']['email']['user'],
                    config['notify']['email']['password'],
                    config['notify']['email']['receiver'],
                    config['notify']['email']['subject'])

            print(rsync_errors)

            # Reset global variables.
            rsync_results = list()
            rsync_errors = list()
            get_copy_list_results = dict()
            get_copy_list_errors = dict()
