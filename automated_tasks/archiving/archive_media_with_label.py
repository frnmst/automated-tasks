#!/usr/bin/env python3
#
# archive_media_with_label.py
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import hashlib
import pathlib
import tabulate
import fpyutils
import shlex

MEDIA = [
    'video-home-system',
    'music-cassette',
    'phonograph-record',
    'blu-ray-disk',
    'compact-disk',
    'betamax',
]


def get_id_as_string(id: int, digits: int) -> str:
    r"""Add zeros pading to the id."""
    formatting = '{number:0' + str(digits) + 'd}'
    return formatting.format(number=id)


def get_checksum(input: str, length: int) -> str:
    r"""Compute a checksum."""
    m = hashlib.blake2b(digest_size=length)
    m.update(input.encode('UTF-8'))
    return m.hexdigest()


def get_upper_label(media: str, id: str, checksum: str,
                    element_separator: str) -> str:
    r"""Compose the upper label."""
    return (media + element_separator + id + element_separator + checksum)


def get_new_file_name(original_name: str, upper_label: str,
                      media_name_and_original_file_name_separator: str) -> str:
    r"""Compose the filename using the upper label."""
    return (pathlib.Path(shlex.quote(original_name)).name +
            media_name_and_original_file_name_separator + upper_label +
            pathlib.Path(shlex.quote(original_name)).suffix)


def get_label(upper_label: str, lower_label: str, separator: str) -> str:
    r"""Get the full label."""
    return upper_label + separator + lower_label


def pipeline(args):
    r"""Run the pipeline."""
    c = fpyutils.yaml.load_configuration(args.config)

    # Get media type.
    for j in c['media']:
        for k in j:
            if k == args.media.replace('-', ' '):
                media = j[k]

    padded_id_as_string = get_id_as_string(args.id, c['id']['digits'])
    file_name_checksum = get_checksum(
        args.file_name, c['checksum']['original file name']['length'])
    upper_label = get_upper_label(media, padded_id_as_string,
                                  file_name_checksum,
                                  c['separator']['elements'])
    new_file_name = get_new_file_name(
        args.file_name, upper_label,
        c['separator']['new name original file name'])
    lower_label = get_checksum(new_file_name,
                               c['checksum']['upper label']['length'])
    label = get_label(upper_label, lower_label,
                      c['separator']['upper label lower label'])

    table = [['Original file name', args.file_name], ['Id', args.id],
             ['Media', args.media], ['New file name', new_file_name],
             ['Label', label]]
    print(tabulate.tabulate(table, tablefmt='fancy_grid'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get the file name and label for archiving',
        allow_abbrev=False)
    parser.add_argument('file_name', help='the original file name')
    parser.add_argument('id', type=int, help='a progressive number')
    parser.add_argument('media', choices=MEDIA, help='a type of media')
    parser.add_argument(
        '--config',
        help=
        'the configuration file. Defaults to ./archive_media_with_label.yaml',
        default='./archive_media_with_label.yaml')

    args = parser.parse_args()

    pipeline(args)
