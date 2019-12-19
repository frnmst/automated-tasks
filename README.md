# automated-tasks

A collection of scripts I have written and/or adapted that I currently
use on my systems as automated tasks.

## Table of contents

<!--TOC-->

- [automated-tasks](#automated-tasks)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [Rules](#rules)
    - [The `_metadata.yaml` file](#the-_metadatayaml-file)
      - [Important YAML keys](#important-yaml-keys)
        - [Running users](#running-users)
    - [Scripts](#scripts)
      - [Meta scripts](#meta-scripts)
        - [Prepare environment](#prepare-environment)
      - [Deploy](#deploy)
      - [Automated tasks scripts](#automated-tasks-scripts)
        - [Shell](#shell)
        - [Python](#python)
  - [See also](#see-also)
  - [LICENSE](#license)

<!--TOC-->

## Description

This repository contains a collection of scripts that I have written and/or adapted.
Releasing them to the public is a way to improve their quality as well as to
simplify their deployment.

Automated tasks run when certain events happen: for example when a flash drive
is connected to the system.

## Rules

- scripts are divided by topic and placed in different directories
  accordingly.

- if files are imported into a script, these will be classified as
  configuration files.

- scripts cannot run without configuration files.

- scripts or systemd unit files are optional: a standalone systemd unit file does the job in some cases.
  In this case configuration files are not needed. Conversely, a script does not need
  a systemd unit file if it is called directly by an external program.

### The `_metadata.yaml` file

`_metadata.yaml` contains important information for the deployment of the scripts.
Before reading on have a look at it.

#### Important YAML keys

- the `*` character matches any value.

| YAML Key | Optional | Optional only if condition | Comment |
|----------|----------|----------------------------|---------|
| `[*][*][configuration files]` | yes | no script is present (see the "Rules" section) | - |
| `[*][*][systemd unit files][paths][service]` | no | - | - |
| `[*][*][systemd unit files][paths][timer]` | yes | - | - |
| `[*][*][dependencies][*][version]` | no | - | the reported version corresponds to a known working one |
| `[*][*][running user]` | no | - | see the *Running users* table |

##### Running users

| User name | Description |
|-----------|-------------|
| `motion` | the user running the [motion](https://motion-project.github.io/index.html) instance |
| `mydesktopuser` | a generic user with Xorg access |
| `myuser` | a generic user with our without Xorg access |
| `root` | the root user |
| `surveillance` | a user running audio and/or video surveillance scripts or programs |
| `yacy` | the user running the [yacy](https://www.yacy.net/) instance |

### Scripts

#### Meta scripts

##### Prepare environment

The `./prepare_environment.py` script outputs a shell script based on the content
of the `./metadata.yaml` file.  All scripts are disabled by default. Have a look
at the `enabled` fields in the metadata file. Once you are done editing you can 
run the script like this

    $ ./prepare_environment.py prepare_environment.conf > prepare_environment.sh

Now, check the `./prepare_environment.sh` before running it as `root`

    # chmod +x ./prepare_environment.sh && ./prepare_environment.sh

This script also copies `./deploy.py`.

#### Deploy

The `./deploy.py` script copies the systemd unit files from the services by-user
directory to the appropriate systemd directory. It also start and enables the
newly copied systemd timer files. If a timer file is not available, the service
file is enabled and started instead.

If needed, edit the hard-coded `SRC_DIR` variable in the script.

#### Automated tasks scripts

##### Shell

- scripts must be bash compatible.
- scripts must start with: `#!/usr/bin/env bash`
- scripts must set these options: `set -euo pipefail`
- all variables must be enclosed in braces
- all variables must be quoted, except integers

##### Python

- scripts must be written in Python 3.
- scripts must start with: `#!/usr/bin/env python3`
- access to the shell must be done with `subprocess.run`
- all shell variables must be quoted with `shlex.quote`
- shell commands must be split with `shlex.split`

## See also

- [From crontabs to Systemd timers](https://frnmst.gitlab.io/notes/from-crontabs-to-systemd-timers.html)
  to learn where and how the the files are placed.

## LICENSE

Unless noted differently:

```
Copyright (C) 2019 Franco Masotti <franco.masotti@live.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
