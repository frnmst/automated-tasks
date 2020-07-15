#!/usr/bin/env bash
#
# android_phone_backup.sh
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

mkdir -p "${SRC}"
mkdir -p "${DST}"
chmod 700 "${SRC}"
chmod 700 "${DST}"

set +e
# If something is already mounted, quit immediately.
exists_mount="$(mount | grep --regexp="fuse.sshfs" | grep --regexp=""${USERNAME}"@"${HOST}":")"
set -e
[ -z "${exists_mount}" ]

set +e
# Mount.
# See https://gist.github.com/mfellner/5743990 for the rsync options
echo "${PASSWORD}" | sshfs -o password_stdin -p ${PORT} \
    "${USERNAME}"@"${HOST}": \
    "${SRC}" \
    && rsync \
    --recursive \
    --verbose \
    --size-only \
    --no-group \
    --no-owner \
    --no-perms \
    --no-times \
    --whole-file \
    --inplace \
    "${SRC}"/* "${DST}"
retval=${?}

# Unmount.
fusermount3 -u "${SRC}"
set -e

if [ ${retval} -eq 0 ]; then
    status='ok'
else
    status='error'
fi

message=""${MESSAGE_PREAMBLE}" ${status} "${MESSAGE_POSTAMBLE}""

if [ "${LOG_TO_STDOUT}" = 'true' ]; then
    printf "%s\n" "${message}"
fi
if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
    curl -X POST \
        ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
        -F "title=${GOTIFY_TITLE}" \
        -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
fi
