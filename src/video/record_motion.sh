#!/usr/bin/env bash
#
# record_motion.sh
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

mkdir -p "${DST_DIRECTORY}"
pushd "${DST_DIRECTORY}"
while true; do
    # Delete videos older than DAYS_TO_KEEP days.
    set +e
    find . -type f -name '*.mkv' -mtime +${DAYS_TO_KEEP} -exec rm -rf {} \;
    set -e

    # Record the video as a motion JPEG incapsulated in a Martoska file.
    # Usually this script is run on the same computer handling the video
    # stream.
    ffmpeg \
        -an \
        -reconnect 1 \
        -reconnect_at_eof 1 \
        -reconnect_streamed 1 \
        -reconnect_delay_max 480 \
        -i "http://"${HOST}":"${PORT}"" \
        -q:v "${QUALITY}" \
        -video_size "${RESOLUTION}" \
        -vframes ${FRAMES_PER_FILE} \
        -vcodec mjpeg \
        ${EXTRA_FFMPEG_OPTIONS} \
        video_"$(date +%F_%T)".mkv
done
popd
