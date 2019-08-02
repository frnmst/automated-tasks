#!/usr/bin/env bash
#
# The MIT License (MIT)
#
# Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>
# Copyright © 2019 Héctor Molinero Fernández
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -euo pipefail

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

HEADER_FILE="${1}"
FOOTER_FILE="${2}"
POST_COMMANDS="${3}"
HBLOCK_DIRECTORY="${4}"

make -C "${HBLOCK_DIRECTORY}" clean

# Update the source code (which includes the block lists).
git pull

ENL="$(printf '\\\nx')"
ENL="${ENL%x}"
"${BLOCK_DIRECTORY}"/hblock \
    --template 'local-zone: "\1" redirect'"$ENL"'local-data: "\1 A \2"' \
    --comment '#' \
    --header "${HEADER_FILE}" \
    --footer "${FOOTER_FILE}" \
    --output /etc/unbound/unbound.conf \
    "${BLOCK_DIRECTORY}"/resources/alt-formats/unbound.conf.sh

. "${POST_COMMANDS}"

# To be able to apply changes, unbound needs to be restarted.
systemctl restart unbound
