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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

for repository in ${!REPOSITORY[@]}; do

    # Get branch names.
    if [ -z "${REPOSITORY["${repository}"]}" ]; then
        # With unspecified branches, scan for all branches
        # and get their changes.
        branches=$(git -C "${repository}" branch --format='%(refname:short)')
    else
        branches=${REPOSITORY["${repository}"]}
    fi

    for branch in ${branches}; do

        # Filter the most recent commits.
        # Separate unrelated fields with newlines.
        message="$(git -C "${repository}"  log  "${branch}" \
            --pretty=format:"%h%n%an%x09<%ae>%n%aI%n%s%n[%b]%n" \
            --since="${CHECK_TIMEOUT_INTERVAL_SECONDS} seconds")"

        # Avoid processing empty messages.
        if [ -n "${message}" ]; then
            if [ "${LOG_TO_STDOUT}" = 'true' ]; then
                printf "%s\n" "${message}"
            fi
            if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
                # Show the directory name of the repository instead of
                # showing the full path.
                curl -X POST \
                    ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
                    -F "title=${branch}@"$(basename ${repository})"" \
                    -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
            fi
        fi
    done
done
