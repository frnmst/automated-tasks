#!/usr/bin/env bash
#
# borgmatic_hooks.sh
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

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

ACTION="${2}"
BORGMATIC_CONFIGURATION_FILENAME="${3}"
REPOSITORY="${4}"
OUTPUT="${5}"
ERROR="${6}"

# Remove most output lines to have a clearer output.
# Useful when running with verbose >= 1.
if [ "${KEEP_LAST_N_OUTPUT_LINES}" = 'true' ]; then
    OUTPUT="$(printf "%s" "${OUTPUT}" | tail -n${NUMBER_OF_OUTPUT_LINES})"
fi

message_body=""${ACTION}" on "${REPOSITORY}" using "${BORGMATIC_CONFIGURATION_FILENAME}": "${OUTPUT}" "${ERROR}""
message=""${MESSAGE_PREAMBLE}" "${message_body}" "${MESSAGE_POSTAMBLE}""

if [ "${LOG_TO_STDOUT}" = 'true' ]; then
    printf "%s\n" "${message}"
fi
if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
    curl -X POST \
        ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
        -F "title=${GOTIFY_TITLE}" \
        -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
fi
if [ "${LOG_TO_EMAIL}" = 'true' ]; then
    if [ "${EMAIL_MESSAGE_AS_PAGER}" = 'true' ]; then
        if [ "${ERROR}" = "${BORGMATIC_EMPTY_ERROR_MESSAGE}" ]; then
            # No error was raised.
            message=""${MESSAGE_PREAMBLE}" "${ACTION}" @"${EMAIL_MESSAGE_AS_PAGER_BACKUP_NAME}": "${EMAIL_MESSAGE_AS_PAGER_OK_MESSAGE}""
        else
            message=""${MESSAGE_PREAMBLE}" "${ACTION}" @"${EMAIL_MESSAGE_AS_PAGER_BACKUP_NAME}": "${EMAIL_MESSAGE_AS_PAGER_ERROR_MESSAGE}""
        fi
    fi
    echo "${message}" | ${EMAIL_COMMAND}
fi
