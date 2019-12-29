# automated-tasks

A collection of scripts I have written and/or adapted that I currently
use on my systems as automated tasks.

## Table of contents

<!--TOC-->

## Description

This repository contains a collection of scripts that I have written and/or adapted.
Releasing them to the public is a way to improve their quality as well as to
simplify their deployment.

Automated tasks run when certain events happen: for example when a flash drive
is connected to the system.

## Documentation

https://frnmst.github.io/automated-tasks/

## Rules

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

## See also

- [From crontabs to Systemd timers](https://frnmst.gitlab.io/notes/from-crontabs-to-systemd-timers.html)
  to learn where and how the the files are placed.

## LICENSE

See the [LICENSE](docs/license.rst) file.
