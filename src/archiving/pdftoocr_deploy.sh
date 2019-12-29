#!/usr/bin/env bash
#
# Copyright (C) 2013 slm @ Stack Exchange (https://unix.stackexchange.com/a/93971)
# Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>
#
# This script is licensed under a
# Creative Commons Attribution-ShareAlike 3.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/3.0/>.

set -euo pipefail

CONFIG="${1}"
INPUT="${2}"
OUTPUT="${3}"

. "${CONFIG}"

[ -f "${INPUT}" ]

rm -rf "${TMP_FILE}"

[ -f "${COLOR_OVERRIDE_FILE}" ] && GRAYSCALE='n'

if [ "${GRAYSCALE}" = 'y' ]; then
    gs \
        -sOutputFile="${TMP_FILE}" \
        -sDEVICE=pdfwrite \
        -sColorConversionStrategy=Gray \
        -dProcessColorModel=/DeviceGray \
        -dCompatibilityLevel=1.4 \
        -dNOPAUSE \
        -dBATCH \
        -dAutoRotatePages=/None \
        "${INPUT}"
else
    cp "${INPUT}" "${TMP_FILE}"
fi

ocrmypdf \
    --skip-text \
    --output-type pdfa \
    --tesseract-timeout 1800 \
    --optimize 3 \
    --remove-vectors \
    --mask-barcodes \
    --threshold \
    --jbig2-lossy \
    --deskew \
    --clean \
    --rotate-pages \
    --sidecar \
    --language "${OCR_LANG}" \
    "${TMP_FILE}" "${OUTPUT}"

rm -rf "${TMP_FILE}" "${COLOR_OVERRIDE_FILE}"
