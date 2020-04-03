#!/usr/bin/env bash
#
# notify_unit_status.sh
#
# Copyright (C) 2015 Pablo Martinez @ Stack Exchange (https://serverfault.com/a/701100)
# Copyright (C) 2018 Davy Landman @ Stack Exchange (https://serverfault.com/a/701100)
# Copyright (C) 2020 Franco Masotti <franco.masotti@live.com>
#
# This script is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.

CONFIG="${1}"
. "${CONFIG}"

UNIT="${2}"

echo "Service failure: ${UNIT}" | ${EMAIL_COMMAND}
