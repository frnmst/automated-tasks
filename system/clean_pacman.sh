#!/usr/bin/env bash
#
# clean_pacman.sh
#
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php/Pacman
# Copyright (C)  Arch Wiki contributors https://wiki.archlinux.org/index.php/Pacman/Tips_and_tricks
# Copyright (C)  2019  Franco Masotti <franco.masotti@live.com>.
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
# A copy of the license is included in the section entitled "GNU
# Free Documentation License".

set -euo pipefail

# Remove cache of uninstalled and installed programs keeping previous 3 pkgs.
paccache --remove --keep 3 --verbose --verbose --verbose
# Remove all cache of uninstalled packages.
paccache --remove --keep 0 --uninstalled --verbose --verbose --verbose

# Find orphans and remove them.
orphans=$(pacman --query --unrequired --deps --quiet) \
    && pacman --remove --nosave --recursive ${orphans} --noconfirm --verbose

sync

