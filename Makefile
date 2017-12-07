# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2017 OpenCraft <contact@opencraft.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Config ######################################################################

WORKERS ?= 3
WORKERS_LOW_PRIORITY ?= 3
SHELL = /bin/bash
HONCHO_MANAGE := honcho run python3 manage.py
HONCHO_MANAGE_TESTS := honcho -e .environ/.env.test run python3 manage.py


# Parameters ##################################################################

# For `test_one` use the rest as arguments and turn them into do-nothing targets
ifeq ($(firstword $(MAKECMDGOALS)),$(filter $(firstword $(MAKECMDGOALS)),test_one manage))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif


# Commands ####################################################################

clean:
	find -name '*.pyc' -delete
	find -name '*~' -delete
	find -name '__pycache__' -type d -delete
	rm -rf .coverage build

manage:
	$(HONCHO_MANAGE) $(RUN_ARGS)

migrate: clean
	$(HONCHO_MANAGE) migrate

# Check for unapplied migrations
migration_check: clean
	!(($(HONCHO_MANAGE) showmigrations | grep '\[ \]') && printf "\n\033[0;31mERROR: Pending migrations found\033[0m\n\n")

migration_autogen: clean
	$(HONCHO_MANAGE) makemigrations

shell:
	HUEY_QUEUE_NAME=accounting_low_priority $(HONCHO_MANAGE) shell_plus

requirements_upgrade:
	pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

requirements_dev:
	pip install -r requirements/dev.txt

# Tests #######################################################################

test_prospector: clean
	prospector --profile accounting --uses django

test: test_prospector
	python3 manage.py test
