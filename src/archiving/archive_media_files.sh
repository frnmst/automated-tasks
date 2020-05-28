#!/usr/bin/env bash
#
# archive_media_files_simple.sh
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php?title=Udisks&oldid=575618
# Copyright (C)  2019-2020  Franco Masotti <franco.masotti@live.com>.
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
#
# See https://en.wikipedia.org/wiki/Comparison_of_file_systems#Metadata
# for a list of supported timestamps for the most common filesystems.
#
# Steps:
#
# 0. use EXIF data DateTimeOriginal
# 1. use EXIF data MediaCreateDate
# 2. use last modification time
# 3, use time of last status change
# 4. use last access time
# 5. use the current date
compute_media_date_path()
{
    local media="${1}"

    computed_path="$(exiftool -quiet -s -s -s -tab -dateformat "${DATE_STRING}" \
        -DateTimeOriginal "${media}")"
    if [ -z "${computed_path}" ]; then
        computed_path="$(exiftool -quiet -s -s -s -tab -dateformat "${DATE_STRING}" \
        -MediaCreateDate "${media}")"
    fi
    if [ -z "${computed_path}" ]; then
        computed_path="$(compute_epoch_to_path "$(stat -c%Y "${media}")" "${DATE_STRING}")"
    fi
    if [ -z "${computed_path}" ]; then
        computed_path="$(compute_epoch_to_path "$(stat -c%Z "${media}")" "${DATE_STRING}")"
    fi
    if [ -z "${computed_path}" ]; then
        computed_path="$(compute_epoch_to_path "$(stat -c%X "${media}")" "${DATE_STRING}")"
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
    local remove_source_files="${8}"

    rsync \
        --chown=${uid_map}:${gid_map} \
        --chmod=D${dir_perm},F${file_perm} \
        --ignore-existing \
        --numeric-ids \
        --archive \
        --verbose \
        --acls \
        --xattrs \
        --hard-links \
        --backup \
        --backup-dir="${dst_base_dir}"_backup \
	${remove_source_files} \
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
    local remove_source_files="${7}"
    local use_file_metadata_as_filename="${8}"

    set -euo pipefail

    if [ "${use_file_metadata_as_filename}" = 'true' ]; then
        DATE_STRING="%F_%T"
        filename="$(compute_media_date_path "${media}")"
    else
        filename="$(basename "${media}")"
    fi

    # Compute subcomponent destination directory as in "year/month".
    DATE_STRING="%Y/%m"
    date_path="$(compute_media_date_path "${media}")"

    # The final destination path of the file.
    media_dst=""${dst_base_dir}"/"${date_path}"/"${filename}""

    media_dst_top_dir="$(dirname "${media_dst}")"
    mkdir -p "${media_dst_top_dir}"

    run_rsync \
        "${media}" \
        "${media_dst}" \
        "${dst_base_dir}" \
        ${uid_map} \
        ${gid_map} \
        ${dir_perm} \
        ${file_perm} \
        "${remove_source_files}"
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
    local remove_source_files="${8}"
    local  use_file_metadata_as_filename="${9}"

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
        -o -iname "*.PNG" \
        -o -iname "*.MP3" \) \
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
        --timeout 99999999999999% \
        --joblog "${log_file}" \
        --env PATH --plain \
        prepare_rsync ::: "${dst_base_dir}" ::: "${uid_map}" ::: "${gid_map}" ::: ${dir_perm} ::: ${file_perm} ::: ${media_files} ::: "${remove_source_files}" ::: "${use_file_metadata_as_filename}"
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

main()
{
    [ ${UID} -eq 0 ]
    print_waiting_uuids

    # Nothing must be mounted before starting the sync.
    umount --lazy "${SRC}" 1>/dev/null 2>/dev/null || :;
    stdbuf --output=L -- udevadm monitor --udev --subsystem-match=block | while read -r -- _ _ event devpath _; do
        if [ "${event}" = 'add' ]; then
            for uuid in ${WHITELIST_UUIDS}; do
                if [ -e "/dev/disk/by-uuid/"${uuid}"" ]; then
                    printf "\n%s\n" "starting "${uuid}""
	                mount "/dev/disk/by-uuid/"${uuid}"" "${SRC}"
                    final_dst_path=""${DST}"/"${uuid}""

                    process "${SRC}" \
                        "${final_dst_path}" \
                        ${UID_MAP} \
                        ${GID_MAP} \
                        ${DIR_PERM} \
                        ${FILE_PERM} \
                        "${LOG_FILE}" \
                        "${remove_source_files}" \
                        "${USE_FILE_METADATA_AS_FILENAME}"

                    # Just in case.
                    sync &

                    # Get the log file and remove table column names.
                    # This variable takes in account all processes, even failed ones.
                    processed_files=$(($(wc --lines "${LOG_FILE}" | awk '{print $1}')-1))
                    cat "${LOG_FILE}"
                    if [ "${DELETE_LOG_FILE}" = 'true' ]; then
                        rm -rf "${LOG_FILE}"
                    fi
                    message=""${MESSAGE_PREAMBLE}" \
"${uuid}" \
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
                    umount --lazy "${SRC}"
                fi
            done
        fi
    done
}

main
