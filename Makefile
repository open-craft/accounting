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

install_system_dependencies: apt_get_update
	sudo -E apt-get install -y `tr -d '\r' < debian_packages.lst`

manage:
	$(HONCHO_MANAGE) $(RUN_ARGS)

migrate: clean
	$(HONCHO_MANAGE) migrate

# Check for unapplied migrations
migration_check: clean
	!(($(HONCHO_MANAGE) showmigrations | grep '\[ \]') && printf "\n\033[0;31mERROR: Pending migrations found\033[0m\n\n")

migration_autogen: clean
	$(HONCHO_MANAGE) makemigrations

run: clean migration_check
	honcho start --concurrency "worker=$(WORKERS),worker_low_priority=$(WORKERS_LOW_PRIORITY)"

rundev: clean migration_check
	honcho start -f Procfile.dev

shell:
	HUEY_QUEUE_NAME=accounting_low_priority $(HONCHO_MANAGE) shell_plus

upgrade_dependencies:
	pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

# Tests #######################################################################

test_prospector: clean
	prospector --profile accounting --uses django

test_migrations_missing: clean
	$(HONCHO_MANAGE_TESTS) makemigrations --dry-run --check

test_one: clean
	$(HONCHO_MANAGE_TESTS) test $(RUN_ARGS)

# TODO: Temporarily 'ok' with 0 coverage. Raise it when we write tests for the first time.
test_unit: clean
	honcho -e .environ/.env.test run coverage run --source='.' --omit='*/tests/*' ./manage.py test --noinput
	coverage html
	@echo -e "\nCoverage HTML report at file://`pwd`/build/coverage/index.html\n"
	@coverage report --fail-under 0 || (echo "\nERROR: Coverage is below 94%\n" && exit 2)

test: clean test_prospector test_unit test_migrations_missing
	@echo -e "\nAll tests OK!\n"
