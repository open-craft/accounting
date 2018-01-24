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
Tests for Account models.
"""

import ddt

from accounting.account.tests import factories
from accounting.common.tests.base import TestCase


@ddt.ddt
class AccountTestCase(TestCase):
    """ Test cases for `models.Account`. """

    def setUp(self):
        """ Set up test objects. """
        self.account = factories.AccountFactory(
            business_name='OpenCraft GmbH',
            user__username='opencraft'
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.account), 'OpenCraft GmbH')


@ddt.ddt
class HourlyRateTestCase(TestCase):
    """ Test cases for `models.HourlyRate`. """

    def setUp(self):
        """ Set up test objects. """
        self.client = factories.AccountFactory(business_name='OpenCraft GmbH')
        self.provider = factories.AccountFactory(business_name='Developer')
        self.hourly_rate = factories.HourlyRateFactory(
            client=self.client,
            provider=self.provider,
            hourly_rate__amount=100,
            hourly_rate__currency='EUR'
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.hourly_rate), 'Developer charges OpenCraft GmbH 100.00 EUR / hour')
