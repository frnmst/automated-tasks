#!/usr/bin/env bash
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

set -euo pipefail

# Get correct path before loading the configuration file.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set the path for the perl command.
PATH=${PATH}:/usr/bin/vendor_perl
command -V exiftool

CONFIG="${1}"
. "${CONFIG}"

pushd "${ROOT_DIRECTORY}"

files="$(find . -type f -name '*.MP4' -mtime +$((${DAYS_TO_KEEP}+1)))"

gpx_files=''
for f in ${files}; do
    printf "%s" "processing ${f} ... "

    # Quick and dirty. If a file is corrupt, just skip it.
    # Also remove the corrupted video.
    exiftool -extractEmbedded "${f}" 1>/dev/null 2>/dev/null || \
        { { [ "${REMOVE_FOOTAGE}" = 'yes' ] && rm "${f}"; }; printf "%s\n" 'KO' && continue; }
    printf "%s\n" 'OK'
    exiftool -extractEmbedded -printFormat ""${DIR}"/gpx.fmt" "${f}" > "${f}".gpx

    # Get all gpx files.
    gpx_files="${gpx_files} "${f}".gpx"
    [ "${REMOVE_FOOTAGE}" = 'yes' ] && rm "${f}"
done

sync

# Remove duplicate gpx files. Since I'm using a dual dashcam, front
# and rear footages might contain the same metadata, thus generating
# equal gpx files.
#
# See:
# https://unix.stackexchange.com/a/192712
# by Tristan Storch
#
# which is licensed under cc by-sa 3.0.
if [ -n "${gpx_files}" ]; then
    sha1sum ${gpx_files} | sort | gawk 'BEGIN{lasthash = ""} $1 == lasthash {print $2} {lasthash = $1}' | xargs rm
fi

sync

popd
