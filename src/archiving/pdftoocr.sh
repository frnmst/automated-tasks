#!/usr/bin/env bash
#
# Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>
#
# This script is licensed under a
# Creative Commons Attribution-ShareAlike 3.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/3.0/>.

set -euo pipefail

# Get correct path before loading the configuration file.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

CONFIG="${1}"
CONFIG_DEPLOY="${2}"

. "${CONFIG}"

[ "${USER}" = "${EXPECTED_USER}" ]

START=$(date +%s)

pushd "${DOCUMENT_DIR}" 1>/dev/null

files="$(find . -type f -name "${INPUT_FILENAME}" -print)"
i=0
for f in ${files}; do
    # Get and move into the directory at depth n where the input file is found.
    subdir="${f%%/out.pdf}"
    pushd "${subdir}" 1>/dev/null

    OUTPUT_FILENAME=""$(printf "%s" "${subdir}" | tr -d './' | sha1sum | awk '{print $1}')".pdf"
    ""${DIR}"/pdftoocr_deploy.sh" "${CONFIG_DEPLOY}" "${INPUT_FILENAME}" "${OUTPUT_FILENAME}"

    # Just in case something gets altered.
    # We expect 2 files here.
    sha512sum "${OUTPUT_FILENAME}" "${OUTPUT_FILENAME}".txt > SHA512SUMS

    popd 1>/dev/null

    # We don't need the original file anymore.
    rm "${f}"

    # Make the directory non deletable. Treat it as an archive.
    chmod -R 500 "${subdir}"
    i=$((${i}+1))
done

END=$(date +%s)

printf "%s\n" "${i} files processed in $((${END}-${START}))s"

popd 1>/dev/null
