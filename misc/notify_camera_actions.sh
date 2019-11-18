#!/usr/bin/env bash
#
# notify_camera_actions.sh
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

set -euo pipefail

CONFIG="${1}"
CAMERA_NAME="${2}"
ACTION="${3}"

. "${CONFIG}"

message=""${MESSAGE_PREAMBLE}" "${CAMERA_NAME}" "${MESSAGE_BODY}" "${ACTION}" "${MESSAGE_POSTAMBLE}""
if [ "${LOG_TO_STDOUT}" = 'true' ]; then
    printf "%s\n" "${message}"
fi
if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
    curl -X POST \
        ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
        -F "title=${GOTIFY_TITLE}" \
        -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
fi

