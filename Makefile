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

default: clean doc

doc:
	pipenv run $(MAKE) -C docs html

install-dev:
	pipenv install

uninstall-dev:
	pipenv --rm

clean:
	pipenv run $(MAKE) -C docs clean

.PHONY: default doc install-dev uninstall-dev clean