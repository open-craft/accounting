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
Tests for the Common application's models.
"""

import datetime

from django.utils import timezone
import freezegun

from accounting.authentication.tests.factories import UserFactory
from accounting.common.tests.base import TestCase

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


class CommonTestCase(TestCase):
    """Tests for `models.Common`."""

    def setUp(self):
        """Set up test objects."""
        super().setUp()
        self.user = UserFactory()

    @freezegun.freeze_time(NOW)
    def test_date_formatted_without_date(self):
        """`date_formatted` returns the date today when the object doesn't have a `date` field."""
        self.assertEqual(self.user.date_formatted, '2018-01-10')
