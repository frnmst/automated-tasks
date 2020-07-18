#!/usr/bin/env python3
#
# archive_invoice_files.py
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


class EmailError(Exception):
    r"""Error."""


def get_attachments(host: str, port: str, username: str, password: str,
                    mailbox: str, subject_filter: str, dst_base_dir: str,
                    ignore_attachments: list):
    r"""Download and save the attachments."""
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
    conn = imaplib.IMAP4_SSL(host=host, port=int(port))
    conn.login(user=username, password=password)
    conn.select(mailbox=mailbox)

    # message_ids is 1-element list of message ids in BytesIO form.
    # Filter by subject and unread emails.
    # See:
    # https://tools.ietf.org/html/rfc2060.html
    # for all the commands and parameters.
    typ, message_ids = conn.search(None, '(SUBJECT "' + subject_filter + '")',
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
                    filename not in ignore_attachments):
                dst_directory = str(pathlib.Path(dst_base_dir, date_part_path))
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
        'write default configuration file': str(),
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
    }

    status = {
        'invoice file': invoice_file,
        'valid checksum': True,
        'valid signature and signers certificate': True,
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
        except fattura_elettronica_reader.exceptions.CannotExtractOriginalP7MFile:
            # Fatal error.
            done = True
            traceback.print_exc()
            sys.exit(1)

    return status


def validate_decoded_invoice_files_struct(struct: list):
    r"""Check if the data structure corresponds to the specifications."""
    for e in struct:
        assert isinstance(struct[e], dict)
        assert 'invoice file' in struct[e]
        assert 'valid checksum' in struct[e]
        assert 'valid signature and signers certificate' in struct[e]
        assert 'file type' in struct[e]
        assert isinstance(struct[e]['invoice file'], str)
        assert isinstance(struct[e]['valid checksum'], bool)
        assert isinstance(struct[e]['valid signature and signers certificate'],
                          str)
        assert isinstance(struct[e]['file type'], str)
        assert struct[e]['file type'] in ['p7m', 'plain']


def decode_invoice_files(file_group: dict) -> list:
    r"""Decode multiple invoice files."""
    invoice_files = list()
    k = 0
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
                invoice_files[k] = status
                k += 1

                # There is no need to try to invert the input files because
                # processing completed correctly.
                done = True

    return invoice_files


def print_invoice(file: dict, invoice_css_string: str, printer: str):
    r"""Print the invoice file."""
    html_file = file['invoice file'] + '.html'
    with tempfile.NamedTemporaryFile() as g:
        css = CSS(string=invoice_css_string)
        html = HTML(html_file)
        temp_name = g.name
        html.write_pdf(temp_name, stylesheets=[css])
        conn = cups.Connection()
        conn.printFile(printer, temp_name, 'invoice', {'media': 'a4'})


def print_status_page(file: str, css_string: str, printer: str,
                      show_script_info: bool, show_openssl_version: bool,
                      info_url: str, show_crypto_status: bool,
                      crypto_status: str, valid_crypto_status_value: str,
                      invalid_crypto_status_value: str,
                      show_checksum_status: str, checksum_status: str,
                      valid_checksum_status_value: str,
                      invalid_checksum_status_value: str,
                      show_p7m_status: bool, p7m_status: str,
                      is_p7m_status_value: str, is_not_p7m_status_value: str):
    r"""Print the status page."""
    html_file = file['invoice file'] + '.html'

    content = '<h1>' + pathlib.Path(html_file).stem + '</h1>'
    if show_script_info:
        content += '<h2>generated by <code>' + info_url + '</code></h2>'
    if show_openssl_version:
        content += '<h2>' + subprocess.run(
            shlex.split('openssl version'),
            capture_output=True).stdout.decode('UTF-8').rstrip() + '</h2> '
    if show_crypto_status:
        if file['valid signature and signers certificate']:
            content += '<h1>' + crypto_status + ' ' + valid_crypto_status_value + '</h1>'
        else:
            content += '<h1>' + crypto_status + ' ' + invalid_crypto_status_value + '</h1>'
    if show_checksum_status:
        if file['valid checksum']:
            content += '<h1>' + checksum_status + ' ' + valid_checksum_status_value + '</h1>'
        else:
            content += '<h1>' + checksum_status + ' ' + invalid_checksum_status_value + '</h1>'
    if show_p7m_status:
        if file['file type'] == 'p7m':
            content += '<h1>' + p7m_status + ' ' + is_p7m_status_value + '</h1>'
        else:
            content += '<h1>' + p7m_status + ' ' + is_not_p7m_status_value + '</h1>'

    with tempfile.NamedTemporaryFile() as g:
        css = CSS(string=css_string)
        html = HTML(string=content)
        temp_name = g.name
        html.write_pdf(temp_name, stylesheets=[css])
        conn = cups.Connection()
        conn.printFile(printer, temp_name, 'invoice', {'media': 'a4'})


if __name__ == '__main__':
    configuration_file = sys.argv[1]
    data = fpyutils.yaml.load_configuration(configuration_file)

    pathlib.Path(data['files']['destination base directory']).mkdir(
        mode=0o700, parents=True, exist_ok=True)
    file_group = get_attachments(
        host=data['certified email']['host'],
        port=data['certified email']['port'],
        username=data['certified email']['username'],
        password=data['certified email']['password'],
        mailbox=data['certified email']['mailbox'],
        subject_filter=data['certified email']['subject filter'],
        dst_base_dir=data['files']['destination base directory'],
        ignore_attachments=data['files']['ignore attachments'])
    decoded_invoice_files = decode_invoice_files(file_group)

    validate_decoded_invoice_files_struct(decoded_invoice_files)
    for f in decoded_invoice_files:
        if data['print']['enabled']:
            print_invoice(f, data['print']['css string'],
                          data['print']['printer'])
            if data['print']['status page']['enabled']:
                print_status_page(
                    f, data['print']['css string'], data['print']['printer'],
                    data['print']['status page']['show script info'],
                    data['print']['status page']['show openssl version'],
                    data['print']['status page']['info url'],
                    data['print']['status page']['crypto status']['enabled'],
                    data['print']['status page']['crypto status']['message'],
                    data['print']['status page']['crypto status']
                    ['valid crypto status value'], data['print']['status page']
                    ['crypto status']['invalid crypto status value'],
                    data['print']['status page']['checksum status']['enabled'],
                    data['print']['status page']['checksum status']['message'],
                    data['print']['status page']['checksum status']
                    ['valid checksum status value'],
                    data['print']['status page']['checksum status']
                    ['invalid checksum status value'],
                    data['print']['status page']['p7m status']['enabled'],
                    data['print']['status page']['p7m status']['message'],
                    data['print']['status page']['p7m status']
                    ['is p7m status value'], data['print']['status page']
                    ['p7m status']['is not p7m status value'])
        if data['notify']['gotify']['enabled']:
            message = 'processed invoice = ' + pathlib.Path(
                f['invoice file']).name
            fpyutils.send_gotify_message(data['notify']['gotify']['url'],
                                         data['notify']['gotify']['token'],
                                         message,
                                         data['notify']['gotify']['title'],
                                         data['notify']['gotify']['priority'])
