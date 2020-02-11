#!/usr/bin/env bash
#
# archive_emails.sh
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php/OfflineIMAP
# Copyright (C)  2019-2020  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".
#
# See also https://github.com/OfflineIMAP/offlineimap/blob/master/offlineimap.conf

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

set +e
offlineimap -u MachineUI -c "${OFFLINEIMAP_CONFIG}" > "${LOG_FILE}"
retval=${?}
transferred_emails=$(grep "msg:copyingmessage" --count "${LOG_FILE}")
set -e

cat "${LOG_FILE}"
if [ "${DELETE_LOG_FILE}" = 'true' ]; then
    rm -rf "${LOG_FILE}"
fi

if [ ${retval} -eq 0 ]; then
    status='ok'
else
    status='error'
fi

message=""${MESSAGE_PREAMBLE}" ${status} (${retval}) "${MESSAGE_POSTAMBLE}" ${transferred_emails}"

if [ "${LOG_TO_STDOUT}" = 'true' ]; then
    printf "%s\n" "${message}"
fi
if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
    curl -X POST \
        ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
        -F "title=${GOTIFY_TITLE}" \
        -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
fi
