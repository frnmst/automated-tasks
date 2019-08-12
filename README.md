# automated-tasks

A collection of scripts I have written and/or adapted that I currently
use on my systems as automated tasks.

## Table of contents

<!--TOC-->

- [automated-tasks](#automated-tasks)
  - [Table of contents](#table-of-contents)
  - [What](#what)
  - [Why](#why)
  - [Rules](#rules)
    - [YAML keys](#yaml-keys)
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

## What

Automated tasks run when certain conditions are met, such as a particular time and
date or when, for example, a USB flash drive is added to the system.

## Why

This repository is a way to improve the quality of these scripts as well as to
simplify the deployment.

## Rules

- Scripts are divided by topic and placed in different directories
  accordingly.

- If files are imported into a script, these will be classified as
  configuration files.

- Scripts cannot run without configuration files.

- Scripts are optional: a standalone systemd unit file does the job in some cases.
  In this case configuration files are not needed.

### Important YAML keys

| YAML Key | Optional | Optional only if condition | Comment |
|----------|----------|----------------------------|---------|
| `[*][*][configuration files]` | yes | no script is present (see the "Rules" section) | - |
| `[*][*][systemd unit files][paths][service]` | no | - | - |
| `[*][*][systemd unit files][paths][timer]` | yes | - | - |
| `[*][*][dependencies][*][version]` | no | - | the reported version corresponds to a known working one |
| `[*][*][running user]` | no | - | possible running users are `root`, `myuser` (a generic user with our without Xorg), `mydesktopuser` (a generic user with Xorg) |

- The `*` character matches any value.

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
