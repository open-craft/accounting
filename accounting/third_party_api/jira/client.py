# -*- coding: utf-8 -*-
#
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

"""
JIRA API client to be used by the Accounting service.
"""

from django.conf import settings
from jira import JIRA as UpstreamJira  # NOQA

from accounting.third_party_api.jira.models import TempoWorklog


class Jira(UpstreamJira):
    """
    A modified version of the upstream JIRA client.

    It has the following changes:

    - Tempo REST API functionality built-in.
    """

    TEMPO_BASE_URL = '{server}/rest/tempo-timesheets/3/{path}'

    def __init__(self, server=settings.JIRA_SERVER_URL, basic_auth=None, **kwargs):
        """
        An override that uses Django settings for certain option parameters.
        """
        if basic_auth is None and settings.JIRA_SERVICE_USER_USERNAME and settings.JIRA_SERVICE_USER_PASSWORD:
            basic_auth = (settings.JIRA_SERVICE_USER_USERNAME, settings.JIRA_SERVICE_USER_PASSWORD)
        super().__init__(server=server, basic_auth=basic_auth, **kwargs)

    def tempo_worklogs(self, jira_username, from_date, to_date):
        """
        Get a list of worklogs from the Tempo REST API for a user and a date range.

        Expects `from_date` and `to_date` to be `datetime` objects.
        """
        response_json = self._get_json('worklogs', base=self.TEMPO_BASE_URL, params={
            'username': jira_username,
            'dateFrom': from_date.strftime('%Y-%m-%d'),
            'dateTo': to_date.strftime('%Y-%m-%d'),
        })
        return [TempoWorklog(raw_worklog_json) for raw_worklog_json in response_json]
