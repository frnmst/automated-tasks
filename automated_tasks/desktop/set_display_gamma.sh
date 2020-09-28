#!/usr/bin/env bash
#
# Copyright (C) 2011 Nimmermehr @ Stack Exchange (https://askubuntu.com/a/62270)
# Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>
#
# This script is licensed under a
# Creative Commons Attribution-ShareAlike 3.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/3.0/>.

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

export DISPLAY="${XORG_DISPLAY_ID}"
/usr/bin/xrandr --output "${DISPLAY_OUTPUT}" --gamma "${GAMMA_OPTION}"
