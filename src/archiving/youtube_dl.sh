#!/usr/bin/env bash
#
# youtube_dl.sh
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
. "${CONFIG}"

mkdir -p "${OUTPUT_DST_DIR}"

pushd "${OUTPUT_DST_DIR}"

# Count the number of initial and final files.
touch "${ARCHIVE_LIST}"
number_of_initial_files=$(wc -l "${ARCHIVE_LIST}" | awk '{print $1}')

set +e
# youtube-dl might not return 0 even if some videos are correctly downloaded.
youtube-dl --verbose --config-location "${YTDL_CONFIG}" --batch "${URLS}" --download-archive "${ARCHIVE_LIST}"
set -e

number_of_deleted_files=0
if [ "${DELETE_OLD_FILES}" = 'true' ]; then
    # For this to work be sure to set the no-mtime option in the options file.
    # Only the video files, infact, would retain the original modification time
    # (not the modification time correpsponding to the download time).
    # All the other files such as thumbnails and subtitles do not retain the
    # original mtime. For this reason it is simpler not to consider the
    # original mtime.
    number_of_deleted_files=$(find . -type f -mtime +$((${DAYS_TO_KEEP}+1)) -exec rm {} \; | wc -l)
fi

number_of_final_files=$(wc -l "${ARCHIVE_LIST}" | awk '{print $1}')
number_of_downloaded_files=$((${number_of_final_files}-${number_of_initial_files}))
message=""${MESSAGE_PREAMBLE}" ${number_of_downloaded_files} "${MESSAGE_POSTAMBLE}" (+${number_of_downloaded_files}-${number_of_deleted_files})"

if [ "${LOG_TO_STDOUT}" = 'true' ]; then
    printf "%s\n" "${message}"
fi
if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
    curl -X POST \
        ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
        -F "title=${GOTIFY_TITLE}" \
        -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
fi

popd

