#!/usr/bin/env bash
#
# archive_media_files_simple.sh
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php?title=Udisks&oldid=575618
# Copyright (C)  2019  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".
#
# Note: this program was inspired by:
# 1. https://github.com/frnmst/automated-tasks/blob/master/archiving/archive_documents_simple.sh
# 2. https://frnmst.gitlab.io/notes/automatic-removable-media-synchronization.html
# both released under the GFDLv1.3+

set -euo pipefail

CONFIG="${1}"
. "${CONFIG}"

[ ${UID} -eq 0 ]

compute_epoch_to_path()
{
    local epoch="${1}"
    local date_string="${2}"

    date -d @${epoch} "+"${date_string}""
}

# Since we are going to use the shoot date to organize the directories
# it needs to be computed using EXIF data.
# If the file does not have EXIF data with coherent date field. Use
# filesystem timestamps instead.
# See https://en.wikipedia.org/wiki/Comparison_of_file_systems#Metadata
# for a list of supported timestamps for the most common filesystems.
# 0. Use EXIF data DateTimeOriginal
# 1. Use EXIF data MediaCreateDate
# 2. Use last modification time
# 3. Use last access time
# 4. Use the current date
compute_media_date_path()
{
    local media="${1}"
    # Compute subcomponent destination directory as in "year/month".
    DATE_STRING="%Y/%m"

    computed_path="$(exiftool -quiet -s -s -s -tab -dateformat "${DATE_STRING}" \
        -DateTimeOriginal "${media}")"
    if [ -z "${computed_path}" ]; then
        computed_path="$(exiftool -quiet -s -s -s -tab -dateformat "${DATE_STRING}" \
        -MediaCreateDate "${media}")"
    fi
    if [ -z "${computed_path}" ]; then
        computed_path="$(compute_epoch_to_path "$(stat -c%X "${media}")" "${DATE_STRING}")"
    fi
    if [ -z "${computed_path}" ]; then
        computed_path="$(compute_epoch_to_path "$(stat -c%Y "${media}")" "${DATE_STRING}")"
    fi
    if [ -z "${computed_path}" ]; then
        computed_path="$(date "+"${DATE_STRING}"")"
    fi

    printf "%s" "${computed_path}"
}

run_rsync()
{
    local src="${1}"
    local dst="${2}"
    local dst_base_dir="${3}"
    local uid_map="${4}"
    local gid_map="${5}"
    local dir_perm="${6}"
    local file_perm="${7}"

    rsync  \
        --quiet \
        --chown=${uid_map}:${gid_map} \
        --chmod=D${dir_perm},F${file_perm} \
        --ignore-existing \
        --backup \
        --backup-dir="${dst_base_dir}"_backup \
        --numeric-ids \
        --archive \
        --verbose \
        --acls \
        --xattrs \
        --hard-links \
        "${src}" "${dst}"
}

prepare_rsync()
{
    local dst_base_dir="${1}"
    local uid_map="${2}"
    local gid_map="${3}"
    local dir_perm="${4}"
    local file_perm="${5}"
    local media="${6}"

    set -euo pipefail

    date_path="$(compute_media_date_path "${media}")"
    # The final destination path of the file.
    media_dst=""${dst_base_dir}"/"${date_path}"/"$(basename "${media}")""

    media_dst_top_dir="$(dirname "${media_dst}")"
    mkdir -p "${media_dst_top_dir}"

    run_rsync \
        "${media}" \
        "${media_dst}" \
        "${dst_base_dir}" \
        ${uid_map} \
        ${gid_map} \
        ${dir_perm} \
        ${file_perm}
}

process()
{
    # The source directory.
    local src_dir="${1}"
    local dst_base_dir="${2}"
    # The uid_map and gid_map.
    local uid_map="${3}"
    local gid_map="${4}"
    local dir_perm="${5}"
    local file_perm="${6}"
    local log_file="${7}"

    mkdir -p "${dst_base_dir}"

    # See https://gist.github.com/jvhaarst/2343281
    # which was put in public domain.
    # See also https://stackoverflow.com/a/7190624
    # which is licensed under cc by-sa 4.0 with attribution required.
    media_files="$(find  "${src_dir}" \
        -type f \
        -not -wholename "*._*" \
        -a \( -iname "*.JPG" \
        -o -iname "*.MOV" \
        -o -iname "*.JPEG" \
        -o -iname "*.CRW" \
        -o -iname "*.THM" \
        -o -iname "*.RW2" \
        -o -iname "*.ARW" \
        -o -iname "*.AVI" \
        -o -iname "*.MOV" \
        -o -iname "*.MP4" \
        -o -iname "*.MTS" \
        -o -iname "*.PNG" \) \
        -exec bash -c 'printf "%q\n" "$@"' sh {} +)"

    # Export variables and functions so they can be read by GNU Parallel.
    export -f prepare_rsync
    export -f compute_media_date_path
    export -f run_rsync
    export -f compute_epoch_to_path

    # To avoid filename with whitespaces being separated into multiple components,
    # change the IFS variable to something more appropriate.
    IFS=$'\n'
    # Add perl paths since we need exiftool.
    PATH_OLD=${PATH}
    PATH=${PATH}:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl
    parallel \
        --joblog "${log_file}" \
        --env PATH --plain \
        prepare_rsync ::: "${dst_base_dir}" ::: "${uid_map}" ::: "${gid_map}" ::: ${dir_perm} ::: ${file_perm} ::: ${media_files} \
        1>/dev/null 2>/dev/null
    PATH=${PATH_OLD}
    unset IFS
}

print_waiting_uuids()
{
    printf "%s\n" 'Waiting for these UUIDs:'
    printf "%s\n" '========================'
    for uuid in ${WHITELIST_UUIDS}; do
        printf "%s\n" "${uuid}"
    done
}

print_waiting_uuids

# Nothing must be mounted before starting the sync.
umount --lazy "${MNT}" 1>/dev/null 2>/dev/null || :;
stdbuf --output=L -- udevadm monitor --udev --subsystem-match=block | while read -r -- _ _ event devpath _; do
    if [ "${event}" = 'add' ]; then
        for uuid in ${WHITELIST_UUIDS}; do
            if [ -e /dev/disk/by-uuid/"${uuid}" ]; then
                printf "\nstarting %s\n" "${uuid}"

                mount "/dev/disk/by-uuid/"${uuid}"" "${MNT}"

                final_dst_path=""${DST}"/"${uuid}""
                user_name="$(getent passwd ${UID_MAP} | cut -d: -f1)"
                group_name="$(getent group ${GID_MAP} | cut -d: -f1)"
                user_home="$(getent passwd "${user_name}" | cut -d: -f6)"
                # sudo must be configured. Export all necessary function to the new environment.
                # See https://stackoverflow.com/a/19002142 (license cc by-sa 4.0 with attribution required, (C) 2013 Karatheodory)
                DECL="$(declare -f process prepare_rsync run_rsync compute_media_date_path compute_epoch_to_path)"
                # Avoid chdir permission problems.
                pushd "${user_home}" 1>/dev/null 2>/dev/null
                sudo --user="${user_name}" bash -c "${DECL}; process "${MNT}" "${final_dst_path}" ${UID_MAP} ${GID_MAP} ${DIR_PERM} ${FILE_PERM} "${LOG_FILE}""
                popd 1>/dev/null 2>/dev/null

                # Just in case.
                sync &

                # Log.
                # Remove table column names. This variable takes in account all
                # processes, even failed ones.
                processed_files=$(($(wc --lines "${LOG_FILE}" | awk '{print $1}')-1))
                cat "${LOG_FILE}"
                if [ "${DELETE_LOG_FILE}" = 'true' ]; then
                    rm -rf "${LOG_FILE}"
                fi
                message=""${MESSAGE_PREAMBLE}" \
${uuid} \
"${MESSAGE_BODY}" \
${processed_files} \
"${MESSAGE_POSTAMBLE}" \
(+${processed_files})"
                if [ "${LOG_TO_STDOUT}" = 'true' ]; then
                    printf "%s\n" "${message}"
                fi
                if [ "${LOG_TO_GOTIFY}" = 'true' ]; then
                    curl -X POST \
                        ""${GOTIFY_URL}"/message?token="${GOTIFY_TOKEN}"" \
                        -F "title=${GOTIFY_TITLE}" \
                        -F "message=${message}" -F "priority="${GOTIFY_PRIORITY}""
                fi

                wait ${!}
                umount --lazy "${MNT}"
            fi
        done
    fi
done

