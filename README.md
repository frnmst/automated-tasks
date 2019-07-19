# automated-tasks

A collection of scripts I have written and/or adapted that I currently
use on my systems as automated tasks.

## Table of contents

<!--TOC-->

- [automated-tasks](#automated-tasks)
  - [Table of contents](#table-of-contents)
  - [What](#what)
  - [Why](#why)
  - [Structure](#structure)
    - [File locations](#file-locations)
    - [Script](#script)
      - [Shell](#shell)
      - [Python](#python)
  - [See also](#see-also)
  - [LICENSE](#license)

<!--TOC-->

## What

Automated tasks run when certain conditions are met, such as a particular time and
date or when, for example, a USB flash drive is added to the system.

## Why

This repository is a way to improve the quality of these scripts as well as to simplify the deployment.

## Structure

### File locations

Scripts are divided by topic and placed in different directories
accordingly. Have a look at the `./metadata.yaml` file.

If multiple files are imported into a script, these will be classified as
configuration files. 

Systemd timer unit files are optional. If a script does not need them, they will
not be present in the `./metadata.yaml` file.

| YAML Key | Optional |
|----------|----------|
| [...][configuration files][paths] | no |
| [...][systemd unit files][paths][service] | no |
| [...][systemd unit files][paths][timer] | yes |

### Script

The `./prepare_environment.py` script outputs a shell script based on the content
of the `./metadata.yaml` file. You can save its output like this

    $ ./prepare_environment.py prepare_environment.conf > deploy.sh

Once you have checked the file you can run it like this

    # chmod +x ./deploy.sh && ./deploy.sh

#### Shell

- scripts must be bash compatible.
- scripts must start with: `#!/usr/bin/env bash`
- scripts must set these options: `set -euo pipefail`
- all variables must be enclosed in braces
- all variables must be quoted, except integers

#### Python

TODO

## See also

- [From crontabs to Systemd timers](https://frnmst.gitlab.io/notes/from-crontabs-to-systemd-timers.html)
  to learn where and how to place the files.

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
