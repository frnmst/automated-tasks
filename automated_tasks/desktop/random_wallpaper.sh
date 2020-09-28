#!/usr/bin/env bash
#
# Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>
#
# This script is licensed under a
# Creative Commons Attribution-ShareAlike 2.5 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/2.5/>.

set -euo pipefail

CONFIG="${1}"

DISPLAY=:0 feh --bg-center "$(shuf -n1 "${CONFIG}" --random-source=/dev/urandom)"
