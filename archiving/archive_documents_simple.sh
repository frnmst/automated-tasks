#!/usr/bin/env bash
#
# archive_documents_simple.sh
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php?title=Udisks&oldid=575618
# Copyright (C)  2019  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".

set -euo pipefail

[ ${UID} -eq 0 ]

CONFIG="${1}"
. "${CONFIG}"

stdbuf --output=L -- udevadm monitor --udev --subsystem-match=block | while read -r -- _ _ event devpath _; do
    if [ "${event}" = 'add' ]; then
        if [ -e /dev/disk/by-uuid/"${UUID}" ]; then
            printf "%s\n" 'start'
            mount /dev/disk/by-uuid/"${UUID}" "${DST}"
            rsync  \
                --numeric-ids \
                --chown=${UID_MAP}:${GID_MAP} \
                --chmod=D${DIR_PERM},F${FILE_PERM} \
                --archive \
                --verbose \
                --compress \
                --acls \
                --xattrs \
                --hard-links \
                --ignore-existing \
                "${SRC}" "${DST}"
            sync
            umount "${DST}"
            printf "%s\n" 'end'
        fi
    fi
done
