#!/usr/bin/env bash

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

mkdir -p "${OUTPUT_DST_DIR}"

pushd "${OUTPUT_DST_DIR}"

# Count the number of initial and final files.
number_of_initial_files=$(wc -l "${ARCHIVE_LIST}" | awk '{print $1}')

set +e
# youtube-dl might not return 0 even if some videos are correctly downloaded.
youtube-dl --verbose --config-location "${YTDL_CONFIG}" --batch "${URLS}" --download-archive "${ARCHIVE_LIST}"
set -e

if [ "${DELETE_OLD_FILES}" = 'true' ]; then
    # For this to work be sure to set the no-mtime option in the options file.
    # Only the video files would have the correct modification time.
    # For this reason it is easier to delete files older than
    # DAYS_TO_KEEP that refer to the actual download time.
    # exec rm
    find . -type f -mtime +$((${DAYS_TO_KEEP}+1)) -exec rm {} \;
fi

number_of_final_files=$(wc -l "${ARCHIVE_LIST}" | awk '{print $1}')
downloaded_files=$((${number_of_final_files}-${number_of_initial_files}))
message=""${MESSAGE_PREAMBLE}" "${downloaded_files}" "${MESSAGE_POSTAMBLE}""
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

