#!/usr/bin/env python3
#
# archive_invoice_files.py
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# See more copyrights and licenses below.
r"""Download, verify, archive and print invoice files."""

import traceback
import sys
import imaplib
import email
import pathlib
import tempfile
import dateutil.parser
from itertools import permutations
import lxml.etree
from weasyprint import (HTML, CSS)
import fattura_elettronica_reader
import cups
import subprocess
import shlex
import fpyutils
import shutil


class EmailError(Exception):
    r"""Error."""


def get_attachments(config: dict):
    r"""Download and save the attachments."""
    validate_config_struct(config)

    # Most of this function comes from
    # https://github.com/markuz/scripts/blob/master/getmail.py
    #
    # This file is part of my scripts project
    #
    # Copyright (c) 2011 Marco Antonio Islas Cruz
    #
    # This script is free software; you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation; either version 2 of the License, or
    # (at your option) any later version.
    #
    # This script is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program; if not, write to the Free Software
    # Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
    #
    # @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
    # @copyright 2011 Marco Antonio Islas Cruz
    # @license   http://www.gnu.org/licenses/gpl.txt
    conn = imaplib.IMAP4_SSL(host=config['certified email']['host'], port=config['certified email']['port'])
    conn.login(user=config['certified email']['username'], password=config['certified email']['password'])
    conn.select(mailbox=config['certified email']['mailbox'])

    # message_ids is 1-element list of message ids in BytesIO form.
    # Filter by subject and unread emails.
    # See:
    # https://tools.ietf.org/html/rfc2060.html
    # for all the commands and parameters.
    typ, message_ids = conn.search(None, '(SUBJECT "' + config['certified email']['subject filter'] + '")',
                                   '(UNSEEN)')
    if typ != 'OK':
        raise EmailError

    # Email id.
    i = 0
    # Group attachments by email so that they can be processed easily.
    saved_files = dict()
    for m_id in message_ids[0].split():
        # Once the message is processed it will be set as SEEN (read).

        # Attachment group.
        saved_files[i] = list()

        # Returned data are tuples of message part envelope and data.
        # data is 1-element list.
        # data [0][0] corresponds to the header,
        # while data[0][1] corresponds to the text.
        # See:
        # https://tools.ietf.org/html/rfc2060.html#page-41
        # in particular the RFC822 and BODY parameters.
        typ, data = conn.fetch(m_id, '(RFC822)')
        if typ != 'OK':
            raise EmailError

        # Load payload in the email data structure.
        text = data[0][1]
        msg = email.message_from_bytes(text)

        # Get the receiving date of the email.
        date = msg['Date']

        # Iterate through all the attachments of the email.
        for part in msg.walk():
            # Skip current element if necessary.
            if part.get_content_maintype() == 'multipart':
                print('iterating down the tree, skipping...')
                continue
            if part.get('Content-Disposition') is None:
                print('unkown content disposition, skipping...')
                continue

            # Get the filename and the content.
            filename = part.get_filename()
            data = part.get_payload(decode=True)

            # Get the year and month in terms of local time when the email
            # was received.
            dt = dateutil.parser.parse(date)
            # Define a subpath of 'year/month'.
            date_part_path = dt.astimezone(
                dateutil.tz.tzlocal()).strftime('%Y/%m')

            if (filename is not None and data and
                    filename not in config['files']['ignore attachments']):
                dst_directory = str(pathlib.Path(config['files']['destination base directory'], date_part_path))
                # Create the final directory.
                pathlib.Path(dst_directory).mkdir(mode=0o700,
                                                  parents=True,
                                                  exist_ok=True)
                # Compute the filename path based on the final directory.
                filename = str(pathlib.Path(dst_directory, filename))

                # Write the attachment content to its file.
                with open(filename, 'wb') as f:
                    f.write(data)
                saved_files[i].append(filename)
            else:
                print(
                    'undefined filename or no attachments, marking as read anyway'
                )
        i += 1

    conn.close()
    conn.logout()

    return saved_files


def decode_invoice_file(file_to_consider: str, invoice_file: str) -> dict:
    r"""Try to decode the invoice file."""
    source = 'invoice'
    file_type = 'p7m'
    data = {
        'patched': True,
        'configuration file': str(),
        'write default configuration file': False,
        'extract attachments': False,
        'invoice xslt type': 'ordinaria',
        'no invoice xml validation': False,
        'force invoice schema file download': False,
        'generate html output': True,
        'invoice filename': invoice_file,
        'no checksum check': False,
        'force invoice xml stylesheet file download': False,
        'ignore attachment extension whitelist': False,
        'ignore attachment filetype whitelist': False,
        'metadata file': file_to_consider,
        'ignore signature check': False,
        'ignore signers certificate check': False,
        'force trusted list file download': False,
        'keep original file': True,
        'ignore assets checksum': False,
    }

    status = {
        'invoice file': invoice_file,
        'valid checksum': True,
        'valid signature and signers certificate': True,
        'valid assets checksum': True,
        'file type': 'p7m',
    }

    # Most probably a metadata file or a non-signed invoice file.
    # Metadata file must have .xml as extension
    # Avoid case sensitivity problems.
    if str(pathlib.PurePath(file_to_consider).suffix).lower() == '.xml':
        done = False
    else:
        done = True
        # Unprocessed.
        status['invoice file'] = str()

    while not done:
        try:
            fattura_elettronica_reader.pipeline(source=source,
                                                file_type=file_type,
                                                data=data)
            done = True
        except fattura_elettronica_reader.exceptions.InvoiceFileChecksumFailed:
            if status['valid checksum']:
                status['valid checksum'] = False
                # Ignore checksum at the next iteration but mark the checksum
                # as invalid.
                data['no checksum check'] = True
        except fattura_elettronica_reader.exceptions.P7MFileNotAuthentic:
            if status['valid signature and signers certificate']:
                status['valid signature and signers certificate'] = False
                data['ignore signature check'] = True
                data['ignore signers certificate check'] = True
        except fattura_elettronica_reader.exceptions.P7MFileDoesNotHaveACoherentCryptographicalSignature:
            if status['file type'] == 'p7m':
                status['file type'] = 'plain'
                file_type = 'plain'
        except lxml.etree.LxmlError:
            # The selected metadata file is the real invoice file.
            # Retry with the next loop from the caller function.
            done = True
            traceback.print_exc()
        except fattura_elettronica_reader.exceptions.AssetsChecksumDoesNotMatch:
            if status['valid assets checksum']:
                status['valid assets checksum'] = False
                data['ignore assets checksum'] = True
        except fattura_elettronica_reader.exceptions.CannotExtractOriginalP7MFile:
            # Fatal error.
            done = True
            traceback.print_exc()
            sys.exit(1)

    return status


def validate_decoded_invoice_files_struct(struct: list):
    r"""Check if the data structure corresponds to the specifications."""
    for e in struct:
        if not isinstance(e, dict):
            raise TypeError
        if 'invoice file' not in e:
            raise ValueError
        if 'valid checksum' not in e:
            raise ValueError
        if 'valid signature and signers certificate' not in e:
            raise ValueError
        if 'valid assets checksum' not in e:
            raise ValueError
        if 'file type' not in e:
            raise ValueError
        if not isinstance(e['invoice file'], str):
            raise TypeError
        if not isinstance(e['valid checksum'], bool):
            raise TypeError
        if not isinstance(e['valid signature and signers certificate'], bool):
            raise TypeError
        if not isinstance(e['valid assets checksum'], bool):
            raise TypeError
        if not isinstance(e['file type'], str):
            raise TypeError
        if e['file type'] not in ['p7m', 'plain']:
            raise ValueError


def validate_config_struct(data: dict):
    r"""Check if the data structure corresponds to the specifications."""
    if 'certified email' not in data:
        raise ValueError
    if 'files' not in data:
        raise ValueError
    if 'print' not in data:
        raise ValueError
    if 'invoice' not in data:
        raise ValueError
    if 'status page' not in data:
        raise ValueError
    if 'notify' not in data:
        raise ValueError

    if 'host' not in data['certified email']:
        raise ValueError
    if 'port' not in data['certified email']:
        raise ValueError
    if 'username' not in data['certified email']:
        raise ValueError
    if 'password' not in data['certified email']:
        raise ValueError
    if 'mailbox' not in data['certified email']:
        raise ValueError
    if 'subject filter' not in data['certified email']:
        raise ValueError

    if 'destination base directory' not in data['files']:
        raise ValueError
    if 'ignore attachments' not in data['files']:
        raise ValueError

    if 'printer' not in data['print']:
        raise ValueError
    if 'css string' not in data['print']:
        raise ValueError

    if 'file' not in data['invoice']:
        raise ValueError

    if 'file' not in data['status page']:
        raise ValueError
    if 'show' not in data['status page']:
        raise ValueError
    if 'status' not in data['status page']:
        raise ValueError

    if 'gotify' not in data['notify']:
        raise ValueError

    if not isinstance(data['certified email']['host'], str):
        raise TypeError
    if not isinstance(data['certified email']['port'], int):
        raise TypeError
    if not isinstance(data['certified email']['username'], str):
        raise TypeError
    if not isinstance(data['certified email']['password'], str):
        raise TypeError
    if not isinstance(data['certified email']['mailbox'], str):
        raise TypeError
    if not isinstance(data['certified email']['subject filter'], str):
        raise TypeError

    if not isinstance(data['files']['destination base directory'], str):
        raise TypeError
    if not isinstance(data['files']['ignore attachments'], list):
        raise TypeError

    if not isinstance(data['print']['printer'], str):
        raise TypeError
    if not isinstance(data['print']['css string'], str):
        raise TypeError

    if 'print' not in data['invoice']['file']:
        raise ValueError

    if 'store' not in data['status page']['file']:
        raise ValueError
    if 'print' not in data['status page']['file']:
        raise ValueError

    if 'info' not in data['status page']['show']:
        raise ValueError
    if 'openssl version' not in data['status page']['show']:
        raise ValueError

    if 'crypto' not in data['status page']['status']:
        raise ValueError
    if 'checksum' not in data['status page']['status']:
        raise ValueError
    if 'p7m' not in data['status page']['status']:
        raise ValueError
    if 'assets' not in data['status page']['status']:
        raise ValueError

    if 'enabled' not in data['notify']['gotify']:
        raise ValueError
    if 'url' not in data['notify']['gotify']:
        raise ValueError
    if 'token' not in data['notify']['gotify']:
        raise ValueError
    if 'message' not in data['notify']['gotify']:
        raise ValueError
    if 'priority' not in data['notify']['gotify']:
        raise ValueError

    for a in data['files']['ignore attachments']:
        if not isinstance(a, str):
            raise TypeError

    if not isinstance(data['invoice']['file']['print'], bool):
        raise TypeError

    if not isinstance(data['status page']['file']['store'], bool):
        raise TypeError
    if not isinstance(data['status page']['file']['print'], bool):
        raise TypeError

    if 'enabled' not in data['status page']['show']['info']:
        raise ValueError
    if 'url' not in data['status page']['show']['info']:
        raise ValueError

    if 'enabled' not in data['status page']['show']['openssl version']:
        raise ValueError

    if 'enabled' not in data['status page']['status']['crypto']:
        raise ValueError
    if 'message' not in data['status page']['status']['crypto']:
        raise ValueError
    if 'valid value' not in data['status page']['status']['crypto']:
        raise ValueError
    if 'invalid value' not in data['status page']['status']['crypto']:
        raise ValueError

    if 'enabled' not in data['status page']['status']['checksum']:
        raise ValueError
    if 'message' not in data['status page']['status']['checksum']:
        raise ValueError
    if 'valid value' not in data['status page']['status']['checksum']:
        raise ValueError
    if 'invalid value' not in data['status page']['status']['checksum']:
        raise ValueError

    if 'enabled' not in data['status page']['status']['p7m']:
        raise ValueError
    if 'message' not in data['status page']['status']['p7m']:
        raise ValueError
    if 'valid value' not in data['status page']['status']['p7m']:
        raise ValueError
    if 'invalid value' not in data['status page']['status']['p7m']:
        raise ValueError

    if 'enabled' not in data['status page']['status']['assets']:
        raise ValueError
    if 'message' not in data['status page']['status']['assets']:
        raise ValueError
    if 'valid value' not in data['status page']['status']['assets']:
        raise ValueError
    if 'invalid value' not in data['status page']['status']['assets']:
        raise ValueError

    if not isinstance(data['status page']['show']['info']['enabled'], bool):
        raise TypeError
    if not isinstance(data['status page']['show']['info']['url'], str):
        raise TypeError

    if not isinstance(data['status page']['show']['openssl version']['enabled'], bool):
        raise TypeError

    if not isinstance(data['status page']['status']['crypto']['enabled'], bool):
        raise TypeError
    if not isinstance(data['status page']['status']['crypto']['message'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['crypto']['valid value'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['crypto']['invalid value'], str):
        raise TypeError

    if not isinstance(data['status page']['status']['checksum']['enabled'], bool):
        raise TypeError
    if not isinstance(data['status page']['status']['checksum']['message'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['checksum']['valid value'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['checksum']['invalid value'], str):
        raise TypeError

    if not isinstance(data['status page']['status']['p7m']['enabled'], bool):
        raise TypeError
    if not isinstance(data['status page']['status']['p7m']['message'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['p7m']['valid value'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['p7m']['invalid value'], str):
        raise TypeError

    if not isinstance(data['status page']['status']['assets']['enabled'], bool):
        raise TypeError
    if not isinstance(data['status page']['status']['assets']['message'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['assets']['valid value'], str):
        raise TypeError
    if not isinstance(data['status page']['status']['assets']['invalid value'], str):
        raise TypeError


def decode_invoice_files(file_group: dict) -> list:
    r"""Decode multiple invoice files."""
    invoice_files = list()
    for i in file_group:
        files = file_group[i]
        perm = permutations(files)
        files_perm = list(perm)

        j = 0
        done = False
        while j < len(files_perm) and not done:
            # Try all permutations.
            metadata_file = files_perm[j][0]
            invoice_file = files_perm[j][1]
            status = decode_invoice_file(metadata_file, invoice_file)
            if status['invoice file'] != str():
                # Ignore unprocessed files.
                invoice_files.append(status)

                # There is no need to try to invert the input files because
                # processing completed correctly.
                done = True
            j += 1

    return invoice_files


def print_file(printer, file, job_name, proprieties):
    r"""Print a file with CUPS."""
    conn = cups.Connection()
    conn.printFile(printer, file, job_name, proprieties)


def print_invoice(file: dict, data: dict):
    r"""Print the invoice file."""
    validate_config_struct(data)

    html_file = file['invoice file'] + '.html'
    with tempfile.NamedTemporaryFile() as g:
        css = CSS(string=data['print']['css string'])
        html = HTML(html_file)
        temp_name = g.name
        html.write_pdf(temp_name, stylesheets=[css])
        print_file(data['print']['printer'], temp_name, 'invoice', {'media': 'a4'})


def get_status_page(file: dict, data: dict):
    r"""Save and print the status page."""
    validate_config_struct(data)

    html_file = file['invoice file'] + '.html'

    content = '<h1>' + pathlib.Path(html_file).stem + '</h1>'
    if data['status page']['show']['info']['enabled']:
        content += '<h2>generated by <code>' + data['status page']['show']['info']['url'] + '</code></h2>'
    if data['status page']['show']['openssl version']['enabled']:
        content += '<h2>' + subprocess.run(
            shlex.split('openssl version'),
            capture_output=True, shell=False).stdout.decode('UTF-8').rstrip() + '</h2> '
    if data['status page']['status']['crypto']['enabled']:
        if file['valid signature and signers certificate']:
            content += '<h1>' + data['status page']['status']['crypto']['message'] + ' ' + data['status page']['status']['crypto']['valid value'] + '</h1>'
        else:
            content += '<h1>' + data['status page']['status']['crypto']['message'] + ' ' + data['status page']['status']['crypto']['invalid value'] + '</h1>'
    if data['status page']['status']['checksum']['enabled']:
        if file['valid checksum']:
            content += '<h1>' + data['status page']['status']['checksum']['message'] + ' ' + data['status page']['status']['checksum']['valid value'] + '</h1>'
        else:
            content += '<h1>' + data['status page']['status']['checksum']['message'] + ' ' + data['status page']['status']['checksum']['invalid value'] + '</h1>'
    if data['status page']['status']['p7m']['enabled']:
        if file['file type'] == 'p7m':
            content += '<h1>' + data['status page']['status']['p7m']['message'] + ' ' + data['status page']['status']['p7m']['valid value'] + '</h1>'
        else:
            content += '<h1>' + data['status page']['status']['p7m']['message'] + ' ' + data['status page']['status']['p7m']['invalid value'] + '</h1>'
    if data['status page']['status']['assets']['enabled']:
        if file['valid assets checksum']:
            content += '<h1>' + data['status page']['status']['assets']['message'] + ' ' + data['status page']['status']['assets']['valid value'] + '</h1>'
        else:
            content += '<h1>' + data['status page']['status']['assets']['message'] + ' ' + data['status page']['status']['assets']['invalid value'] + '</h1>'

    # Save and print.
    with tempfile.TemporaryDirectory() as tmpdirname:
        css = CSS(string=data['print']['css string'])
        html = HTML(string=content)
        status_page_tmp_path = str(pathlib.Path(tmpdirname, 'status_page.pdf'))
        html.write_pdf(status_page_tmp_path, stylesheets=[css])
        if data['status page']['file']['print']:
            print_file(data['print']['printer'], status_page_tmp_path, 'status page',
                       {'media': 'a4'})
        if data['status page']['file']['store']:
            dir = pathlib.Path(file['invoice file']).parent
            shutil.move(
                status_page_tmp_path,
                str(
                    pathlib.Path(dir,
                                 file['invoice file'] + '_status_page.pdf')))


if __name__ == '__main__':
    configuration_file = sys.argv[1]
    data = fpyutils.yaml.load_configuration(configuration_file)

    validate_config_struct(data)

    pathlib.Path(data['files']['destination base directory']).mkdir(
        mode=0o700, parents=True, exist_ok=True)
    file_group = get_attachments(data)
    decoded_invoice_files = decode_invoice_files(file_group)

    validate_decoded_invoice_files_struct(decoded_invoice_files)
    for f in decoded_invoice_files:
        if data['invoice']['file']['print']:
            print_invoice(f, data)
        get_status_page(f, data)
        if data['notify']['gotify']['enabled']:
            message = 'processed invoice = ' + pathlib.Path(
                f['invoice file']).name
            fpyutils.send_gotify_message(data['notify']['gotify']['url'],
                                         data['notify']['gotify']['token'],
                                         message,
                                         data['notify']['gotify']['title'],
                                         data['notify']['gotify']['priority'])
