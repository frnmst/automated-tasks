#!/usr/bin/env bash

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

mkdir -p "${OUTPUT_DST_DIR}"

pushd "${OUTPUT_DST_DIR}"
youtube-dl --verbose --config-location "${YTDL_CONFIG}" --batch "${URLS}" --download-archive "${ARCHIVE_LIST}"

if [ "${DELETE_OLD_FILES}" = 'true' ]; then
    # For this to work be sure to set the no-mtime option in the options file.
    # Only the video files would have the correct modification time.
    # For this reason it is easier to delete files older than
    # DAYS_TO_KEEP that refer to the actual download time.
    # exec rm
    find . -type f -mtime +$((${DAYS_TO_KEEP}+1)) -exec rm {} \;
fi

popd
