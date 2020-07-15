#!/usr/bin/env make
#
# Makefile
#
# Copyright (C) 2019-2020 frnmst (Franco Masotti) <franco.masotti@live.com>
#
# This file is part of automated-tasks.
#
# automated-tasks is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# automated-tasks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with automated-tasks.  If not, see <http://www.gnu.org/licenses/>.
#

default: pep doc test

pep:
	pipenv run yapf --style '{based_on_style: pep8; indent_width: 4; split_before_logical_operator: False}' -i src/*/*.py utils/*.py
	pipenv run flake8 --ignore=E501,W503,W504 src/*/*.py utils/*.py

doc:
	pipenv run $(MAKE) -C docs html

install:
	pip3 install . --user

uninstall:
	pip3 install automated_tasks

install-dev:
	pipenv install

uninstall-dev:
	pipenv --rm

test:
	pipenv run python setup.py test

clean:
	pipenv run $(MAKE) -C docs clean

.PHONY: default pep doc install-dev uninstall-dev clean
