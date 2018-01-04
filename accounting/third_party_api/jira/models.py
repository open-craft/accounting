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
JIRA-related models.
"""

from decimal import Decimal

from django.db.backends.utils import format_number


class TempoWorklog:
    """
    A worklog "model" reflecting the worklogs that the Tempo API returns.

    This does not require a DB back-end because it's only used to give an easily accessible structure to the
    data returned by the Tempo API. In other words, it serves as an intermediate data structure between code
    in the Accounting service that uses the JIRA client, and the Tempo API endpoint's raw data.

    For clarity, this is an example item returned:

    {
        "timeSpentSeconds": 180,
        "dateStarted": "2017-12-01T00:00:00.000",
        "comment": "Do a bunch of crazy work",
        "self": "https://jira.company.com/rest/api/2/tempo-timesheets/3/worklogs/9994",
        "id": 9993,
        "author": {
            "self": "https://jira.company.com/rest/api/2/user?username=umanshahzad",
            "name": "umanshahzad",
            "key": "umanshahzad",
            "displayName": "Uman Shahzad",
            "avatar": "https://jira.company.com/secure/useravatar?size=small&ownerId=umanshahzad&avatarId=9992"
        },
        "issue": {
            "self": "https://jira.company.com/rest/api/2/issue/9991",
            "id": 9991,
            "projectId": 9999,
            "key": "OC-9999",
            "remainingEstimateSeconds": 0,
            "issueType": {
                "name": "Story",
                "iconUrl": "https://jira.company.com/secure/viewavatar?size=xsmall&avatarId=9992&avatarType=issuetype"
            },
            "summary": "Crazy Work"
        },
        "worklogAttributes": [],
        "workAttributeValues": []
    }

    For a fuller example with some other details, see https://tempo.io/doc/timesheets/api/rest/latest/#848933329
    """

    def __init__(self, raw_worklog):
        """
        Accept a raw worklog and initiate an internal model for easily accessing that data.
        """
        self._worklog = raw_worklog

    def __str__(self):
        """
        Show the ID, key, description, and time spent in hours of this worklog.
        """
        return '({id}) {key}: {description} - {time_spent}h'.format(
            id=self.worklog_id, key=self.issue_key, description=self.description, time_spent=self.time_spent,
        )

    def __repr__(self):
        """
        The representation of this tempo worklog.
        """
        return self.__str__()

    @property
    def time_spent_seconds(self):
        """
        Return the time spent for the worklog in seconds.
        """
        return self._worklog['timeSpentSeconds']

    @property
    def time_spent(self):
        """
        Return the time spent for the worklog in hours.
        """
        return Decimal(format_number(self.time_spent_seconds / 3600.0, 12, 8))

    @property
    def description(self):
        """
        Return the worklog description.
        """
        return self._worklog['comment']

    @property
    def issue_key(self):
        """
        Return the key of the issue, i.e. OC-XYZW.
        """
        return self._worklog['issue']['key']

    @property
    def issue_title(self):
        """
        Return the title of the issue.
        """
        return self._worklog['issue']['summary']

    @property
    def worklog_id(self):
        """
        Return the JIRA Worklog ID for this worklog.
        """
        return self._worklog['id']
