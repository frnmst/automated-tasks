#!/usr/bin/env bash
#
# record_motion.sh
#
# Copyright (C) 2019-2020 Franco Masotti <franco.masotti@live.com>
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

if [ -z "${QUALITY}" ]; then
    quality="-global_quality "${GLOBAL_QUALITY}""
else
    quality="-q:v "${QUALITY}""
fi

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
        ${EXTRA_FFMPEG_OPTIONS_PRE} \
        -an \
        -i "http://"${HOST}":"${PORT}"" \
        ${quality} \
        -video_size "${RESOLUTION}" \
        -c:v "${VIDEO_CODEC}" \
        -vframes ${FRAMES_PER_FILE} \
        ${EXTRA_FFMPEG_OPTIONS} \
        video_"$(date +%F_%T)".mkv
done
popd
