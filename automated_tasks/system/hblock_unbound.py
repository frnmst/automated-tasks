#!/usr/bin/env python3
#
# hblock_unbound.py
#
# The MIT License (MIT)
#
# Copyright (C) 2019-2020 Franco Masotti <franco.masotti@live.com>
# Copyright © 2019 Héctor Molinero Fernández
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
r"""Filter domains."""

import fpyutils
import sys
import shlex

if __name__ == '__main__':
    configuration_file = shlex.quote(sys.argv[1])
    config = fpyutils.yaml.load_configuration(configuration_file)
    header_file = shlex.quote(config['files']['header file'])
    footer_file = shlex.quote(config['files']['footer file'])
    output_file = shlex.quote(config['files']['output file'])
    post_commands_file = shlex.quote(config['files']['post commands file'])
    hblock_root_directory = shlex.quote(
        config['files']['hblock root directory'])

    # Update the source code and the block lists.
    command = 'make -C ' + hblock_root_directory + ' clean && git -C ' + hblock_root_directory + ' pull'
    fpyutils.shell.execute_command_live_output(command)

    # Use unicode to avoid quotes mess.
    template = shlex.quote('local-zone: "' + '\u005C' + '1" redirect' +
                           '\u005C' + '\u000A' + 'local-data: "' + '\u005C' +
                           '1 A ' + '\u005C' + '2"')
    command = ('pushd ' + hblock_root_directory + '; ./hblock --template ' +
               template + ' --comment "#" --header ' + header_file +
               ' --footer ' + footer_file + ' --output ' + output_file +
               ' ./resources/alt-formats/unbound.conf.sh; popd')
    fpyutils.shell.execute_command_live_output(command)

    with open(post_commands_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        fpyutils.shell.execute_command_live_output(line)

    message = 'hblock unbound completed'
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
