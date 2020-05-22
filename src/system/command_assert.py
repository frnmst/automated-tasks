#!/usr/bin/env python3
#
# command_assert.py
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

import requests
import subprocess
import shlex
import re
import sys
import yaml
import requests
import smtplib
import ssl
from email.utils import formatdate
from email.mime.text import MIMEText

def run_command(command: str,
                file_descriptor: str,
                process_timeout_interval: int = 60,
                process_in_timeout_retval: int = -131072,
                process_in_timeout_output: str = '<--##--##-->',
                ) -> tuple:
    r"""Run the command and capture the selected output and return value."""
    assert file_descriptor in ['stderr', 'stdout', 'both']

    command = shlex.split(command)
    try:
        # No exception is raised unless the process goes in timeout.
        result = subprocess.run(command, capture_output=True, timeout=process_timeout_interval)
        if file_descriptor == 'stdout':
            output = result.stdout
        elif file_descriptor == 'stderr':
            output = result.stderr
        elif file_descriptor == 'both':
            output = result.stdout + result.stderr
        output = output.decode('UTF-8')
        retval = result.returncode
    except subprocess.TimeoutExpired:
        output = process_in_timeout_output
        retval = process_in_timeout_retval

    return output, retval

def assert_output(output: str,
                  expected_output: str,
                  retval: int,
                  expected_retval: int,
                  strict_matching = False) -> bool:
    """Check that the output and the return value correspond to expected values."""
    # Escape special regex characters.
    expected_output = re.escape(expected_output)

    if strict_matching:
        assertion_passes = re.match(expected_output, output) is not None and retval == expected_retval
    else:
        # Similar to grep.
        assertion_passes = re.search(expected_output, output) is not None and retval == expected_retval

    return assertion_passes

######################
# Notification hooks #
######################
def send_gotify_notification(name: str,
                             message_status: str,
                             gotify_url: str,
                             gotify_token: str,
                             gotify_title: str,
                             gotify_message: str,
                             gotify_priority: int):
    """Send a notification to a gotify server."""
    # A very simple string concatenation to compute the URL. It is up to the user to
    # configure the variables correctly.
    message = name + ' returned: ' + message_status
    full_url = gotify_url + 'message?token=' + gotify_token
    payload = {
        'title': gotify_title,
        'message': gotify_message + '\n\n' + message,
        'priority': int(gotify_priority),
    }
    requests.post(full_url, json=payload)

def send_email_notification(name: str,
                            message_status: str,
                            email_smtp_server: str,
                            email_port: int,
                            email_sender: str,
                            email_user: str,
                            email_password: str,
                            email_receiver: str,
                            email_subject: str):
    """Send an email."""
    # https://stackoverflow.com/questions/36832632/sending-mail-via-smtplib-loses-time
    #
    # Copyright (C) 2016 tfv @ Stack Overflow (https://stackoverflow.com/a/36834904)
    # Copyright (C) 2017 recolic @ Stack Overflow (https://stackoverflow.com/a/36834904)
    # Copyright (C) 2020 Franco Masotti <franco.masotti@live.com>
    #
    # This script is licensed under a
    # Creative Commons Attribution-ShareAlike 4.0 International License.
    #
    # You should have received a copy of the license along with this
    # work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
    message = name + ' returned: ' + message_status
    msg = MIMEText(message)
    msg['Subject'] = email_subject
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Date'] = formatdate(localtime=True)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(email_smtp_server, email_port, context=context) as conn:
        conn.login(email_user, email_password)
        conn.sendmail(email_sender, email_receiver, msg.as_string())

def pipeline():
    # Load the configuration.
    configuration_file = shlex.quote(sys.argv[1])
    with open(configuration_file, 'r') as f:
        configuration = yaml.load(f, Loader=yaml.SafeLoader)
    dry_run = configuration['dry run']
    commands = configuration['commands']
    process_in_timeout = configuration['process in timeout']
    # Gotify section.
    log_to_gotify = configuration['notifications']['gotify']['log']
    if log_to_gotify:
        gotify_url = configuration['notifications']['gotify']['url']
        gotify_token = configuration['notifications']['gotify']['token']
        gotify_title = configuration['notifications']['gotify']['title']
        gotify_message = configuration['notifications']['gotify']['message']
        gotify_priority = configuration['notifications']['gotify']['priority']
    # Email section.
    log_to_email = configuration['notifications']['email']['log']
    if log_to_email:
        email_smtp_server = configuration['notifications']['email']['smtp server']
        email_port = configuration['notifications']['email']['port']
        email_sender = configuration['notifications']['email']['sender']
        email_user = configuration['notifications']['email']['user']
        email_password = configuration['notifications']['email']['password']
        email_receiver = configuration['notifications']['email']['receiver']
        email_subject = configuration['notifications']['email']['subject']

    for command_data in commands:
        output, retval = run_command(
            commands[command_data]['command'],
            commands[command_data]['file descriptor'],
            commands[command_data]['timeout interval'],
            process_in_timeout['retval'],
            process_in_timeout['output'],
        )
        assertion_passes = assert_output(
            output,
            commands[command_data]['expected output'],
            retval,
            commands[command_data]['expected retval'],
            commands[command_data]['strict matching'])
        if assertion_passes:
            result = configuration['message status']['ok']
        else:
            result = configuration['message status']['error']

        # Check if we can log successful results.
        if not (not commands[command_data]['log if ok'] and assertion_passes):
            if dry_run:
                print (command_data + ' returned: ' + result)
            else:
                if log_to_gotify:
                    send_gotify_notification(command_data, result, gotify_url, gotify_token, gotify_title, gotify_message, gotify_priority)
                if log_to_email:
                    send_email_notification(command_data, result, email_smtp_server, email_port, email_sender, email_user, email_password, email_receiver, email_subject)

if __name__ == '__main__':
    pipeline()
