#!/usr/bin/env python3
#
# convert_videos.py
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
#
# ======================================================================
#
# Original notice
#
# Encode/transcode a video - see http://linuxtv.org/wiki/index.php/V4L_capturing
#
# Approximate system requirements for the default settings:
# * about 10GB disk space for every hour of the initial recording
# * about 1-2GB disk space for every hour of transcoded recordings
# * dual 1.5GHz processor
#
# V4L Capture Script - encode and transcode video
# Written between 2015 and 2020 by Andrew Sayers <v4l-capture-script@pileofstuff.org>
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
r"""Encode and transcode videos from various sources."""

import argparse
import shlex
import pathlib
import yaml
import datetime
import fpyutils

#########
# Utils #
#########


def filter_directories(data: dict) -> list:
    r"""Do a filter on the subdirectories to decide which files need to be transcoded."""
    assert_configuration_struct(data)

    directories_to_transcode = list()
    encoding_complete_file = data['file outputs']['base'][
        'encoding complete file']
    p = pathlib.Path(data['file outputs']['base']['base output dir'])

    # 1. filter the directories with the encoding complete file.
    fs = p.rglob(encoding_complete_file)

    for f in fs:
        # Get the parent directory.
        parent = f.parent

        if f.is_file():
            # 2. keep directories without the lockfile and without the.
            # transcoding complete file.
            if (pathlib.Path(
                    parent, data['file outputs']['base']
                ['transcoding complete file']).is_file() or pathlib.Path(
                    parent, data['file outputs']['base']
                    ['transcoding lock file']).is_file()):
                print('locked or transcoding complete, skipping: ' +
                      str(parent))
            else:
                directories_to_transcode.append(str(parent))

    return directories_to_transcode


############
# Encoding #
############


def pre_encode_v4l(data: dict, dry_run: bool = False) -> int:
    r"""Set input proprieties for a v4l device."""
    assert_configuration_struct(data)

    return fpyutils.shell.execute_command_live_output(
        'v4l2-ctl --set-input ' + data['video']['device']['extra']['input'] +
        ' --set-ctrl ' + data['video']['device']['extra']['controls'] +
        ' --device ' + data['video']['device']['base']['path'],
        dry_run=dry_run)


def post_encode(data: dict):
    r"""Run the post-encode actions."""
    assert_configuration_struct(data)

    pathlib.Path(data['file outputs']['base']
                 ['encoding complete file full path']).touch(0o700,
                                                             exist_ok=True)

    # Write the encoding profile.
    with open(data['file outputs']['base']['encoding complete file full path'],
              'w') as f:
        yaml.dump(data, f)


def read_encoding_profile(data: dict) -> str:
    r"""Read the encoding profile from the encoded metafile."""
    assert_configuration_struct(data)

    # Load the encoding profile.
    data = fpyutils.yaml.load_configuration(
        data['file outputs']['base']['encoding complete file full path'])
    return data['profile']


###############
# Transcoding #
###############


def pre_transcode(data: dict) -> str:
    r"""Run the pre-transcode actions."""
    assert_configuration_struct(data)

    pathlib.Path(
        data['file outputs']['base']['transcoding lock file full path']).touch(
            0o700, exist_ok=True)


def post_transcode(data: dict):
    r"""Run the post-transcode actions."""
    assert_configuration_struct(data)

    pathlib.Path(data['file outputs']['base']
                 ['transcoding complete file full path']).touch(0o700,
                                                                exist_ok=True)
    pathlib.Path(data['file outputs']['base']
                 ['transcoding lock file full path']).unlink(missing_ok=True)


def post_transcode_with_description(data: dict):
    r"""Run the post-transcode actions."""
    assert_configuration_struct(data)
    pathlib.Path(data['file outputs']['base']
                 ['transcoding description complete file full path']).touch(
                     0o700, exist_ok=True)


def common_transcode_action(data: dict, args: argparse.Namespace) -> tuple:
    r"""Transcode."""
    assert_configuration_struct(data)

    # Iterate directories to find the encoding_complete
    # and transcoding_complete files.
    command = str()
    profile = str()
    filtered_directories = filter_directories(data)
    for directory in filtered_directories:
        patch_configuration(data, args.action, directory)
        profile = read_encoding_profile(data)

        # Match encoding profile.
        if profile == args.profile:

            if not args.dry_run:
                pre_transcode(data)

            command += transcode(data)
            command += ' && '

            if pathlib.Path(data['file outputs']['base']
                            ['description file full path']).is_file():
                command += add_description(data) + ' && '

    # Remove the last ' && ' from the string.
    command = command[:-len(' && ')]

    return filtered_directories, profile, command


#######
# v4l #
#######


def encode_v4l(data: dict, duration: str) -> str:
    r"""Encode a video from a v4l device."""
    assert_configuration_struct(data)

    return (
        'ffmpeg -i <( gst-launch-1.0 -q v4l2src device=' +
        data['video']['device']['base']['path'] + ' do-timestamp=true norm=' +
        data['video']['device']['extra']['tv norm'] +
        ' pixel-aspect-ratio=1 ! ' +
        data['video']['device']['extra']['capabilities'] +
        ' ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! mux. alsasrc device='
        + data['audio']['device']['base']['path'] + ' do-timestamp=true ! ' +
        data['audio']['device']['extra']['capabilities'] +
        ' ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! mux. matroskamux name=mux ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! fdsink fd=1)'
        + ' -y -c:v ' + data['video']['action']['format'] + ' ' +
        data['video']['action']['options'] + ' -y -c:a ' +
        data['audio']['action']['format'] + ' ' +
        data['audio']['action']['options'] + ' -f ' +
        data['muxer']['action']['format'] + ' ' +
        data['muxer']['action']['options'] + ' ' + '-threads ' +
        data['generic options']['action']['threads'] + ' -t ' + duration +
        ' ' + data['file outputs']['base']['encoded file full path'])


def stream_v4l(data: dict):
    r"""Stream a video from a v4l device."""
    assert_configuration_struct(data)

    return (
        'cvlc v4l2:// :v4l2-dev=' + data['video']['device']['base']['path'] +
        ' :v4l2-width=' + data['video']['action']['width'] + ' :v4l2-height=' +
        data['video']['action']['height'] + ' :v4l2-standard=' +
        data['video']['action']['standard'] + ' :v4l2-input=' +
        data['video']['device']['extra']['input'] + ' :input-slave=alsa://' +
        data['audio']['device']['base']['path'] +
        ''' --sout "#transcode{threads=''' +
        data['generic options']['action']['threads'] +
        ',vcodec=mp4v,acodec=mpga,vb=' + data['video']['action']['bitrate'] +
        ',ab=' + data['audio']['action']['bitrate'] + ',samplerate=' +
        data['audio']['action']['sample rate'] +
        ',venc=ffmpeg{keyint=20,hurry-up,vt=800000},deinterlace}:standard{access=http,mux=ogg,dst='
        + data['generic options']['action']['host'] + ':' +
        data['generic options']['action']['port'] + '''}" --ttl 12''')


#######
# DVD #
#######


def encode_dvd(data: dict) -> str:
    r"""Encode a video from a DVD device.

    ..note:: part of this process includes transcoding.
    """
    assert_configuration_struct(data)

    return ('HandBrakeCLI --verbose --input ' +
            data['video']['device']['base']['path'] + ' --output ' +
            data['file outputs']['base']['encoded file full path'] +
            ' --encoder ' + data['video']['action']['format'] + ' --format ' +
            data['muxer']['action']['format'] + ' --aencoder ' +
            data['audio']['action']['format'] + ' --preset ' +
            data['generic options']['action']['preset'] + ' ' +
            data['generic options']['action']['subtitles'] + ' ' +
            data['generic options']['action']['chapters'] + ' ' +
            data['generic options']['action']['title'] + ' ' +
            data['video']['action']['options'] + ' ' +
            data['audio']['action']['options'])


def stream_dvd(data: dict) -> str:
    r"""Stream a video from a DVD device.

    ..note:: this functionality might be slow and laggy.
    """
    assert_configuration_struct(data)

    return ('cvlc dvdsimple://' + data['video']['device']['base']['path'] +
            ''' --sout "#standard{access=http,mux=ogg,dst=''' +
            data['generic options']['action']['host'] + ':' +
            data['generic options']['action']['port'] + '''}" --ttl 12''')


##########
# common #
##########


def transcode(data: dict) -> str:
    r"""Transcode video files."""
    assert_configuration_struct(data)

    return ('ffmpeg -i ' +
            data['file outputs']['base']['encoded file full path'] +
            ' -y -c:v ' + data['video']['action']['format'] + ' ' +
            data['video']['action']['options'] + ' -y -c:a ' +
            data['audio']['action']['format'] + ' ' +
            data['audio']['action']['options'] + ' -f ' +
            data['muxer']['action']['format'] + ' ' +
            data['muxer']['action']['options'] + ' ' + '-threads ' +
            data['generic options']['action']['threads'] + ' ' +
            data['file outputs']['base']['transcoded file full path'])


def sum_time_index_to_offset_seconds(time_index: str = '00:00:00',
                                     offset_seconds: int = 0) -> str:
    r"""Sum seconds to a time index."""
    return datetime.datetime.strftime(
        datetime.datetime.strptime(time_index, '%H:%M:%S') +
        datetime.timedelta(seconds=offset_seconds), '%H:%M:%S')


def write_description_srt_file(
    data: dict,
    description: str,
    id: int,
    start_time: str,
    end_time: str,
):
    r"""Write the SRT file."""
    assert_configuration_struct(data)
    assert id >= 1

    # Create a new file for each run and append new descriptions to it.
    if id == 1:
        mode = 'w'
    else:
        mode = 'a'

    with open(data['file outputs']['base']['description file full path'],
              mode) as f:
        f.write(str(id))
        f.write('\n')
        f.write(start_time + ',000 --> ' + end_time + ',000')
        f.write('\n')
        f.write(description)
        f.write('\n\n')


def build_srt_file_structure(data: dict, descriptions: list):
    r"""Do the time index computation to write the SRT file."""
    assert_configuration_struct(data)
    for d in descriptions:
        assert isinstance(d, str)

    offset = 0
    id = 1
    base = '00:00:00'
    start = '00:00:00'
    end = '00:00:00'
    for d in descriptions:
        start = sum_time_index_to_offset_seconds(base, offset)
        end = sum_time_index_to_offset_seconds(
            end, data['generic options']['action']['description duration'])
        write_description_srt_file(data, d, id, start, end)
        offset += data['generic options']['action']['description duration']
        id += 1


def add_description(data: dict):
    r"""Put a video description using a new embedded srt subtitle track."""
    assert_configuration_struct(data)

    return (
        'ffmpeg -i ' +
        data['file outputs']['base']['transcoded file full path'] + ' -i ' +
        data['file outputs']['base']['description file full path'] +
        ' -map 0 -c:v copy -c:a copy -c:s copy -map 1 -c:s subrip -metadata:s:s language='
        + data['generic options']['action']['description track name'] + ' ' +
        data['file outputs']['base']
        ['transcoded file with description full path'])


def assert_configuration_struct(data: dict):
    r"""Verify that the data structure corresponds to the specifications."""
    assert 'action' in data
    assert 'file outputs' in data
    assert 'base' in data['file outputs']
    assert 'extra' in data['file outputs']
    if data['patched']:
        assert 'encoded file full path' in data['file outputs']['base']
        assert 'transcoded file full path' in data['file outputs']['base']
        assert 'encoding complete file full path' in data['file outputs'][
            'base']
        assert 'transcoding complete file full path' in data['file outputs'][
            'base']
        assert 'transcoded file with description full path' in data[
            'file outputs']['base']
        assert 'transcoding description complete file full path' in data[
            'file outputs']['base']
        assert 'transcoding lock file full path' in data['file outputs'][
            'base']
        assert 'base output dir full path' in data['file outputs']['base']

    # Video.
    assert 'video' in data
    assert 'device' in data['video']
    assert 'base' in data['video']['device']
    assert 'path' in data['video']['device']['base']
    assert 'extra' in data['video']['device']
    assert 'action' in data['video']

    # Audio.
    assert 'audio' in data
    assert 'device' in data['audio']
    assert 'base' in data['audio']['device']
    assert 'path' in data['audio']['device']['base']
    assert 'extra' in data['audio']['device']
    assert 'action' in data['audio']

    assert 'action' in data['muxer']

    assert 'generic options' in data

    assert 'action' in data['generic options']

    if data['action'] == 'encode':
        assert 'description start' in data['generic options']['action']
        assert 'description duration' in data['generic options']['action']
    elif data['action'] == 'transcode':
        assert 'description track name' in data['generic options']['action']


def populate_configuration(data: dict, source: str, profile: str,
                           action: str) -> dict:
    r"""Filter the relevant data for the current session."""
    # 1. get the generic options.
    f = data['profile'][source][profile]['file outputs']['name']
    file_outputs_base = data['file outputs']['base'][f]
    file_outputs_extra = data['file outputs']['extra'][f]

    # 2. get the hardware devices.
    d = data['profile'][source][profile]['devices']
    d_video_name = d['video']['name']
    d_audio_name = d['audio']['name']
    device_video_base = data['device']['video']['base'][d_video_name]
    device_audio_base = data['device']['audio']['base'][d_audio_name]
    device_video_extra = data['device']['video']['extra'][d_video_name]
    device_audio_extra = data['device']['audio']['extra'][d_audio_name]

    # 3. get the action.
    a = data['profile'][source][profile]['actions'][action]
    a_video_name = a['video']['name']
    a_audio_name = a['audio']['name']
    a_muxer_name = a['muxer']['name']
    a_generic_options_name = a['generic options']['name']
    action_video = data[action]['video'][a_video_name]
    action_audio = data[action]['audio'][a_audio_name]
    action_muxer = data[action]['muxer'][a_muxer_name]
    action_generic_options = data[action]['generic options'][
        a_generic_options_name]

    # 4. populate the data structure.
    return {
        # If this dictionary is modified later
        # the patched variable needs to be updated.
        'patched': False,
        'profile': profile,
        'action': action,
        'file outputs': {
            'base': file_outputs_base,
            'extra': file_outputs_extra,
        },
        'video': {
            'device': {
                'base': device_video_base,
                'extra': device_video_extra,
            },
            'action': action_video,
        },
        'audio': {
            'device': {
                'base': device_audio_base,
                'extra': device_audio_extra,
            },
            'action': action_audio,
        },
        'muxer': {
            'action': action_muxer,
        },
        'generic options': {
            'action': action_generic_options,
        },
    }


def patch_configuration(data: dict, action: str, file_directory: str):
    r"""Add and change elements to the data structure."""
    assert_configuration_struct(data)

    data['action'] = action

    base_dir = str(
        pathlib.Path(
            shlex.quote(data['file outputs']['base']['base output dir']),
            shlex.quote(file_directory)))
    base_dir = shlex.quote(base_dir)
    data['file outputs']['base']['base output dir full path'] = base_dir

    data['file outputs']['base']['encoded file full path'] = str(
        pathlib.Path(base_dir,
                     shlex.quote(
                         data['file outputs']['base']['encoded file'])))
    data['file outputs']['base']['transcoded file full path'] = str(
        pathlib.Path(
            base_dir,
            shlex.quote(data['file outputs']['base']['transcoded file'])))
    data['file outputs']['base'][
        'transcoded file with description full path'] = str(
            pathlib.Path(
                base_dir,
                shlex.quote(data['file outputs']['base']
                            ['transcoded file with description'])))
    data['file outputs']['base']['encoding complete file full path'] = str(
        pathlib.Path(
            base_dir,
            shlex.quote(
                data['file outputs']['base']['encoding complete file'])))
    data['file outputs']['base']['transcoding complete file full path'] = str(
        pathlib.Path(
            base_dir,
            shlex.quote(
                data['file outputs']['base']['transcoding complete file'])))
    data['file outputs']['base'][
        'transcoding description complete file full path'] = str(
            pathlib.Path(
                base_dir,
                shlex.quote(data['file outputs']['base']
                            ['transcoding description complete file'])))
    data['file outputs']['base']['transcoding lock file full path'] = str(
        pathlib.Path(
            base_dir,
            shlex.quote(
                data['file outputs']['base']['transcoding lock file'])))
    data['file outputs']['base']['description file full path'] = str(
        pathlib.Path(
            base_dir,
            shlex.quote(data['file outputs']['base']['description file'])))

    # Mark the data structure as updated.
    data['patched'] = True


def pipeline(args: argparse.Namespace):
    r"""Run the pipeline."""
    c = fpyutils.yaml.load_configuration(args.config)
    data = populate_configuration(c, args.source, args.profile, args.action)
    output_dir = fpyutils.path.gen_pseudorandom_path(args.output_dir_suffix)
    patch_configuration(data, args.action, output_dir)
    pre_stream_v4l = pre_encode_v4l

    if args.action == 'stream':
        if args.source == 'dvd':
            command = stream_dvd(data)
        elif args.source == 'v4l':
            pre_stream_v4l(data, args.dry_run)
            command = stream_v4l(data)

    elif args.action == 'encode':
        if args.source == 'dvd':
            command = encode_dvd(data)
        elif args.source == 'v4l':
            pre_encode_v4l(data, args.dry_run)
            command = encode_v4l(data, args.duration)

        if not args.dry_run:
            pathlib.Path(
                shlex.quote(data['file outputs']['base']
                            ['base output dir full path'])).mkdir(
                                mode=0o700, parents=True, exist_ok=True)
            if args.description is not None:
                build_srt_file_structure(data, args.description)

    elif args.action == 'transcode':
        filtered_directories, profile, command = common_transcode_action(
            data, args)

    retcode = fpyutils.shell.execute_command_live_output(command,
                                                         dry_run=args.dry_run)
    if not args.dry_run:
        # All commands must be successful before
        # continuing with the post actions.
        if retcode == 0:
            if args.action == 'encode':
                post_encode(data)
            elif args.action == 'transcode':
                for directory in filtered_directories:

                    # Match the encoding profile.
                    if profile == args.profile:
                        patch_configuration(data, args.action, directory)
                        post_transcode(data)
                        post_transcode_with_description(data)


if __name__ == '__main__':
    program_description = 'Capture, encode and transcode videos from different sources'
    parser = argparse.ArgumentParser(description=program_description,
                                     allow_abbrev=False)
    source_subparsers = parser.add_subparsers(title='source',
                                              dest='source',
                                              required=True)

    ###########
    # Sources #
    ###########
    dvd_parser = source_subparsers.add_parser('dvd', help='DVD device')
    v4l_parser = source_subparsers.add_parser('v4l', help='v4l device')

    #######
    # DVD #
    #######
    dvd_subparsers = dvd_parser.add_subparsers(title='action',
                                               dest='action',
                                               required=True)

    dvd_rip_parser = dvd_subparsers.add_parser('rip',
                                               aliases=['encode'],
                                               help='rip the DVD')
    help_rip_output_dir_suffix = 'specify a prefix for directory name so that it can be easily identified. Defaults to ""'
    dvd_rip_parser.add_argument(
        '--output-dir-suffix',
        default=str(),
        help=help_rip_output_dir_suffix,
    )

    help_rip_description = 'add a video description as an extra embedded subtitle track. This option may be specified multiple times'
    dvd_rip_parser.add_argument(
        '--description',
        action='append',
        default=None,
        help=help_rip_description,
    )

    dvd_stream_parser = dvd_subparsers.add_parser(
        'stream', help='stream the content over HTTP for a quick preview')

    help_stream_duration = 'stop streaming at the specified time frame. Use the hh:mm:ss format'
    dvd_stream_parser.add_argument(
        '--duration',
        help=help_stream_duration,
    )

    dvd_transcode_parser = dvd_subparsers.add_parser(
        'transcode',
        help=('transcode all files encoded with the specified profile'))

    #######
    # v4l #
    #######
    v4l_subparsers = v4l_parser.add_subparsers(title='action',
                                               dest='action',
                                               required=True)

    v4l_encode_parser = v4l_subparsers.add_parser(
        'encode', help='capture the output from a v4l and ALSA device')

    help_encode_duration = 'stop encoding at the specified time frame. Use the hh:mm:ss format'
    v4l_encode_parser.add_argument(
        'duration',
        help=help_encode_duration,
    )

    help_encode_output_dir_suffix = 'specify a prefix for directory name so that it can be easily identified. Defaults to ""'
    v4l_encode_parser.add_argument(
        '--output-dir-suffix',
        default=str(),
        help=help_encode_output_dir_suffix,
    )

    help_encode_description = 'add a video description as an extra embedded subtitle track. This option may be specified multiple times'
    v4l_encode_parser.add_argument(
        '--description',
        action='append',
        default=None,
        help=help_encode_description,
    )

    v4l_stream_parser = v4l_subparsers.add_parser(
        'stream', help='stream the content over HTTP for a quick preview')

    help_stream_duration = 'stop streaming at the specified time frame. Use the hh:mm:ss format'
    v4l_stream_parser.add_argument(
        '--duration',
        help=help_stream_duration,
    )

    v4l_transcode_parser = v4l_subparsers.add_parser(
        'transcode',
        help='transcode all files encoded with the specified profile')

    ##########
    # Common #
    ##########
    help_config = 'the path to configuration file. Defaults to ./convert_videos.yaml'
    parser.add_argument('--config',
                        help=help_config,
                        default='./convert_videos.yaml')

    parser.add_argument(
        '--profile',
        help='the name of the settings profile. Defaults to "default"',
        default='default')

    parser.add_argument('--dry-run',
                        action='store_true',
                        help='print the main command instead of executing it')

    parser.set_defaults(output_dir_suffix=str())
    args = parser.parse_args()

    pipeline(args)
