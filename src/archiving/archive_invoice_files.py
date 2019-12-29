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

import configparser
import sys
import imaplib
import email
import pathlib
import tempfile
import dateutil.parser
from itertools import permutations
import requests
import lxml.etree
from weasyprint import (HTML, CSS)
import fattura_elettronica_reader
import cups
import subprocess
import shlex

class EmailError(Exception):
    """Error."""


class InvoiceError(Exception):
    """Error."""


class XMLParsingError(Exception):
    """Error."""


def create_base_directory(path: pathlib.Path):
    """Create the root directory where the invoice files will be located."""
    path.mkdir(mode=0o700, parents=True, exist_ok=True)

def get_attachments(host: str,
            port: str,
            username: str,
            password: str,
            mailbox: str,
            subject_filter: str,
            dst_base_dir: str,
            ignore_attachments: list):
    """Download and save attachments."""
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
    typ, message_ids = conn.search(None, '(SUBJECT "' + subject_filter + '")', '(UNSEEN)')
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
                print ('iterating down the tree, skipping...')
                continue
            if part.get('Content-Disposition') is None:
                print ('unkown content disposition, skipping...')
                continue

            # Get the filename and the content.
            filename = part.get_filename()
            data = part.get_payload(decode=True)

            # Get the year and month in terms of local time when the email
            # was received.
            dt = dateutil.parser.parse(date)
            # Define a subpath of 'year/month'.
            date_part_path = dt.astimezone(dateutil.tz.tzlocal()).strftime('%Y/%m')
            dst_directory = pathlib.Path(dst_base_dir, date_part_path)

            if (filename is not None and data
                and filename not in ignore_attachments):
                # Create the final directory.
                create_base_directory(dst_directory)
                # Compute the filename path based on the final directory.
                filename = str(pathlib.Path(dst_directory, filename))

                # Write the attachment content to its file.
                with open(filename, 'wb') as f:
                    f.write(data)
                saved_files[i].append(filename)
            else:
                print ('undefined filename or no attachments, marking as read anyway')
        i+=1

    conn.close()
    conn.logout()

    return saved_files

def decode_invoice_file(metadata_file: str, invoice_file: str, ignore_crypto_checks=False):
    """Decode and save the invoice file."""
    # Most probably a metadata file or a non-signed invoice file.
    # Metadata file must have .xml as extension
    # Avoid case sensitivity problems.
    valid_signature = True
    if str(pathlib.PurePath(metadata_file).suffix).lower() == '.xml':
        try:
            # Some invoice files might not have the correct filename.
            # Instead of gathering the filename from the metadata file,
            # pass it directly.
            fattura_elettronica_reader.pipeline(metadata_file=metadata_file,
                                                keep_original_invoice=False,
                                                force_trusted_list_file_download=True,
                                                force_invoice_xml_stylesheet_file_download=True,
                                                invoice_filename=invoice_file,
                                                generate_html_output=True)
        except lxml.etree.LxmlError:
            # The selected metadata file is the real invoice file.
            # Retry with the next loop.
            raise XMLParsingError
        except fattura_elettronica_reader.InvoiceFileNotAuthentic:
            if ignore_crypto_checks:
                # If the user specified to ignore cryptographical checks try anyway.
                # There is not need to re-download the trusted list and the stylesheet here.
                try:
                    fattura_elettronica_reader.pipeline(metadata_file=metadata_file,
                                                        keep_original_invoice=False,
                                                        invoice_filename=invoice_file,
                                                        generate_html_output=True,
                                                        ignore_signature_check=True,
                                                        ignore_signers_certificate_check=True)
                    valid_signature = False
                except lxml.etree.LxmlError:
                    # A generic XML parsing error.
                    raise XMLParsingError
                except (fattura_elettronica_reader.XMLFileNotConformingToSchema,
                         fattura_elettronica_reader.CannotExtractOriginalInvoiceFile,
                         fattura_elettronica_reader.InvoiceFileChecksumFailed,
                         fattura_elettronica_reader.MissingTagInMetadataFile):
                    raise InvoiceError
            else:
                # If the signature is not valid and the user decided to keep crypto checks,
                # then fail.
                raise InvoiceError
        except fattura_elettronica_reader.InvoiceFileDoesNotHaveACoherentCryptographicalSignature:
            # Invoice file is a plain XML file.
            try:
                fattura_elettronica_reader.pipeline(metadata_file=metadata_file,
                                                    keep_original_invoice=False,
                                                    invoice_filename=invoice_file,
                                                    generate_html_output=True,
                                                    invoice_file_is_not_p7m=True)
            except lxml.etree.LxmlError:
                # A generic XML parsing error.
                raise XMLParsingError
            except (fattura_elettronica_reader.XMLFileNotConformingToSchema,
                    fattura_elettronica_reader.CannotExtractOriginalInvoiceFile,
                    fattura_elettronica_reader.InvoiceFileChecksumFailed,
                    fattura_elettronica_reader.MissingTagInMetadataFile):
                raise InvoiceError
        except (fattura_elettronica_reader.XMLFileNotConformingToSchema,
                fattura_elettronica_reader.CannotExtractOriginalInvoiceFile,
                fattura_elettronica_reader.InvoiceFileChecksumFailed,
                fattura_elettronica_reader.MissingTagInMetadataFile):
            raise InvoiceError
    else:
        # Ignore unprocessed files.
        invoice_file = str()

    return invoice_file, valid_signature


def validate_processed_invoice_files_struct(files: dict):
    assert isinstance(files, dict)
    for f in files:
        assert isinstance(f, str)
        assert 'valid signature' in files[f]
        assert isinstance(files[f]['valid signature'], bool)


def decode_invoice_files(file_group: dict, ingore_crypto_checks):
    """Decode multiple invoice files."""
    invoice_files = dict()
    for i in file_group:
        files = file_group[i]
        perm = permutations(files)

        for i in list(perm):

            # Try all permutations.
            metadata_file = i[0]
            invoice_file = i[1]

            try:
                processed_invoice_file, valid_signature = decode_invoice_file(metadata_file, invoice_file, ignore_crypto_checks)
                if processed_invoice_file != str():
                    # Ignore unprocessed files.
                    invoice_files[processed_invoice_file] = dict()
                    invoice_files[processed_invoice_file]['valid signature']=valid_signature

                    # There is no need to try to invert the input files because
                    # processing completed correctly.
                    break
            except Exception as e:
                print (e)

    return invoice_files


def print_files(files: dict,
                printer: str,
                print_status_page: bool,
                show_script_info: bool,
                show_crypto_status: bool,
                crypto_status: str,
                valid_crypto_status_value: str,
                invalid_crypto_status_value: str,
                show_openssl_version: bool,
                status_page_css_string: str,
                invoice_css_string : str):
    r"""Transform HTML files into PDF and print them.

    Optionally print the status page.
    """
    conn = cups.Connection()
    for f in files:
        html_filename = f + '.html'
        with tempfile.NamedTemporaryFile() as g:
            # Print the invoice file.
            css = CSS(string=invoice_css_string)
            html = HTML(html_filename)
            temp_name = g.name
            html.write_pdf(temp_name, stylesheets=[css])
            conn.printFile(printer, temp_name, 'invoice', {'media': 'a4'})

        if print_status_page:
            with tempfile.NamedTemporaryFile() as g:
                # Print the status page.
                content = '<h1>' + pathlib.Path(html_filename).stem + '</h1>'
                if show_script_info:
                    content += '<h2>generated by <code>https://github.com/frnmst/automated-tasks/blob/master/archiving/archive_invoice_files.py</code></h2>'
                if show_openssl_version:
                    content += '<h2>' + subprocess.run(shlex.split('openssl version'), capture_output=True).stdout.decode('UTF-8').rstrip() + '</h2> '
                if show_crypto_status:
                    if files[f]['valid signature']:
                        content += '<h1>' + crypto_status + ' ' + valid_crypto_status_value + '</h1>'
                    else:
                        content += '<h1>' + crypto_status + ' ' + invalid_crypto_status_value + '</h1>'
                css = CSS(string=status_page_css_string)
                html = HTML(string=content)
                temp_name = g.name
                html.write_pdf(temp_name, stylesheets=[css])
                conn.printFile(printer, temp_name, 'invoice', {'media': 'a4'})


def get_relative_paths(absolute_paths: list):
    """Get a list of relative paths given the absoulte paths."""
    relative_paths = list()
    for p in absolute_paths:
        relative_paths.append(pathlib.Path(p).name)

    return relative_paths

def send_gotify_notification(processed_files: list,
                             html_files: list,
                             gotify_url: str,
                             gotify_token: str,
                             gotify_title: str,
                             gotify_message: str,
                             gotify_priority: str):
    """Send a notification to a gotify server."""
    # A very simple string concatenation to compute the URL. It is up to the user to
    # configure the variables correctly.
    message = 'processed invoices = ' + ' '.join(processed_files)
    message += '\n'
    message += 'processed html invoices = ' + ' '.join(html_files)
    message += '\n'
    message += '(+' + str(len(processed_files)) + ' +' + str(len(html_files)) + ')'
    full_url = gotify_url + 'message?token=' + gotify_token
    payload = dict()
    payload['title'] = gotify_title
    payload['message'] = gotify_message + '\n\n' + message
    payload['priority'] = int(gotify_priority)
    resp = requests.post(full_url, json=payload)


if __name__ == '__main__':
    configuration_file = sys.argv[1]
    config = configparser.ConfigParser()

    # Load the configuration file.
    config.read(configuration_file)
    host = config['imap']['host']
    port = config['imap']['port']
    username = config['imap']['username']
    password = config['imap']['password']
    mailbox = config['imap']['mailbox']
    subject_filter = config['imap']['subject']
    dst_base_dir = config['files']['dst base dir']
    ignore_attachments = config['files']['ignore attachments'].split(',')
    ignore_crypto_checks = config['files'].getboolean('ignore crypto checks')

    print_invoices = config['print'].getboolean('enable')
    if print_invoices:
        printer = config['print']['printer']
        invoice_css_string = config['print']['css string']

    print_status_page = config['print status page'].getboolean('enable')
    if print_status_page:
        show_script_info = config['print status page'].getboolean('show script info')
        show_openssl_version = config['print status page'].getboolean('show openssl version')
        show_crypto_status = config['print status page'].getboolean('show crypto status')
        crypto_status = config['print status page']['crypto status']
        valid_crypto_status_value = config['print status page']['valid crypto status value']
        invalid_crypto_status_value = config['print status page']['invalid crypto status value']
        status_page_css_string = config['print status page']['css string']

    log_to_gotify = config['notify'].getboolean('log to gotify')
    if log_to_gotify:
        gotify_url = config['notify']['gotify url']
        gotify_token = config['notify']['gotify token']
        gotify_title = config['notify']['gotify title']
        gotify_message = config['notify']['gotify message']
        gotify_priority = config['notify']['gotify priority']

    # Pipeline.
    p = pathlib.Path(dst_base_dir)
    create_base_directory(p)
    file_group = get_attachments(host = host,
            port = port,
            username = username,
            password = password,
            mailbox = mailbox,
            subject_filter = subject_filter,
            dst_base_dir = dst_base_dir,
            ignore_attachments = ignore_attachments)

    processed_invoice_files = decode_invoice_files(file_group, ignore_crypto_checks)

    validate_processed_invoice_files_struct(processed_invoice_files)

    if print_invoices:
        print_files(processed_invoice_files,
            printer,
            print_status_page,
            show_script_info,
            show_crypto_status,
            crypto_status,
            valid_crypto_status_value,
            invalid_crypto_status_value,
            show_openssl_version,
            status_page_css_string,
            invoice_css_string)

    processed_invoice_files_list = list()
    processed_invoice_html_files_list = list()
    for p in processed_invoice_files:
        processed_invoice_files_list.append(p)
        processed_invoice_html_files_list.append(p + '.html')
    processed_invoice_files_relative = get_relative_paths(processed_invoice_files_list)
    processed_invoice_html_files_relative = get_relative_paths(processed_invoice_html_files_list)
    if log_to_gotify:
        send_gotify_notification(processed_invoice_files_relative, processed_invoice_html_files_relative, gotify_url, gotify_token, gotify_title, gotify_message, gotify_priority)

