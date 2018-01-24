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
Tests for Address models.
"""

import ddt

from accounting.address.tests import factories
from accounting.common.tests.base import TestCase


@ddt.ddt
class AddressTestCase(TestCase):
    """ Test cases for `models.Address`. """

    def setUp(self):
        """ Set up test objects. """
        self.address = factories.AddressFactory(
            country='PK',
            address_line1='Address Line 1',
            address_line2='Address Line 2',
            zipcode='99999',
            city='City',
            state='State',
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.address), 'Address Line 1 Address Line 2, City State 99999, PK')
