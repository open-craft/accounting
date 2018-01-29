# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2017-2018 OpenCraft <contact@opencraft.com>
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

# Any configuration variable can be overridden with `VARIABLE = VALUE` in a git-ignored `private.mk` file.

.DEFAULT_GOAL := help
HELP_SPACING ?= 30
COVERAGE_THRESHOLD ?= 81
WORKERS ?= 3
WORKERS_LOW_PRIORITY ?= 3
SHELL ?= /bin/bash
HONCHO_MANAGE := honcho run python3 manage.py
HONCHO_MANAGE_TESTS := honcho -e .environ/.env.test run python3 manage.py

# Parameters ##################################################################

# For `test.one` use the rest as arguments and turn them into do-nothing targets
ifeq ($(firstword $(MAKECMDGOALS)),$(filter $(firstword $(MAKECMDGOALS)),test.one manage))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

# Commands ####################################################################

help: ## Display this help message.
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-$(HELP_SPACING)s\033[0m %s\n", $$1, $$2}'

clean: ## Remove all temporary files.
	find -name '*.pyc' -delete
	find -name '*~' -delete
	find -name '__pycache__' -type d -delete
	rm -rf .coverage build

install_system_dependencies: ## Install system-level dependencies from `debian_packages.lst`. Ignores comments.
	sudo -E apt-get install -y `grep -v '^#' debian_packages.lst | tr -d '\r'`

.PHONY: static
static: ## Collect static files for production.
	$(HONCHO_MANAGE) collectstatic --clear --no-input

manage: ## Run a management command.
	$(HONCHO_MANAGE) $(RUN_ARGS)

migrate: clean ## Run migrations.
	$(HONCHO_MANAGE) migrate

migrations.check: clean ## Check for unapplied migrations.
	@!(($(HONCHO_MANAGE) showmigrations | grep '\[ \]') && printf "\n\033[0;31mERROR: Pending migrations found\033[0m\n\n")

migrations: clean ## Generate migrations.
	$(HONCHO_MANAGE) makemigrations

run: clean migrations.check static translations.compile ## Run the accounting service in a production setting with concurrency.
	honcho start --port 1786 --concurrency "worker=$(WORKERS),worker_low_priority=$(WORKERS_LOW_PRIORITY)"

run.dev: clean migrations.check static translations.compile ## Run the developmental server using `runserver_plus`. Different than docker.
	honcho start --port 1786 -f Procfile.dev

shell: ## Start the power shell.
	HUEY_QUEUE_NAME=accounting_low_priority $(HONCHO_MANAGE) shell_plus

requirements.upgrade: ## Upgrade to the latest dependencies.
	pip-compile

requirements.update: ## Update your virtualenv requirements to perfectly match what's required by the service
	pip-sync

isort: ## Sort all imports in the project by a standard. See .isort.cfg for configuration.
	isort --recursive accounting

translations: ## Make .po files for all existing languages.
	$(HONCHO_MANAGE) makemessages --all -v1

translations.compile: ## Compile .mo files from existing .po files.
	$(HONCHO_MANAGE) compilemessages

# Tests #######################################################################

test.quality: clean ## Run quality tests.
	isort --check-only --recursive accounting
	prospector --profile accounting --uses django

test.migrations_missing: clean ## Check if migrations are missing.
	@$(HONCHO_MANAGE_TESTS) makemigrations --dry-run --check

test.one: clean ## Run tests for a specific path.
	$(HONCHO_MANAGE_TESTS) test $(RUN_ARGS)

test.unit: clean ## Run all unit tests.
	@honcho -e .environ/.env.test run coverage run --source='.' --omit='*/tests/*' ./manage.py test --noinput
	coverage html
	@echo "\nCoverage HTML report at file://`pwd`/build/coverage/index.html\n"
	@coverage report --fail-under $(COVERAGE_THRESHOLD) || (echo "\nERROR: Coverage is below $(COVERAGE_THRESHOLD)%\n" && exit 2)

test: clean test.quality test.migrations_missing test.unit ## Run all tests.
	@echo "\nAll tests OK!\n"

# We ignore `private.mk` so you can define your own make targets, or override some.
include *.mk

# Include `private.mk` last to make sure to override anything.
ifneq ("$(wildchar private.mk)","")
	include private.mk
endif
