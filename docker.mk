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

dev.build: ## Build containers.
	docker-compose build

dev.up: static translations.compile ## Bring up all containers.
	docker-compose up -d

dev.%.up: static translations.compile ## Bring up a specific container.
	docker-compose up $*

dev.down: ## Bring down all containers.
	docker-compose -f docker-compose.yml down

dev.stop: ## Stop all containers.
	docker-compose stop

dev.%.stop: ## Stop a service. Requires *service* name, not container name; i.e. use `web` for the accounting container.
	docker-compose stop $*

dev.logs: ## See and follow logs of all services.
	docker-compose logs -f

dev.%.logs: ## See logs of a service. Requires *service* name, not container name. i.e. use `web` for the accounting container.
	docker-compose logs -f --tail=500 $*

dev.%.shell: ## Shell into the docker container.
	docker exec -i -t $* /bin/bash
