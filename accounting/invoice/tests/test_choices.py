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
Invoice choices tests.
"""

import datetime

from django.utils import timezone
import ddt
import freezegun

from accounting.common.tests.base import TestCase
from accounting.invoice import choices

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


class InvoiceApprovalTestCase(TestCase):
    """ Test cases for `choices.InvoiceApproval`. """

    def test_approved_choices(self):
        """ The approved choices list matches those choices that actually count as being approved. """
        self.assertEqual(choices.InvoiceApproval.approved_choices(), ['automatically', 'manually'])

    def test_not_approved_choices(self):
        """ The not-approved choices list matches those choices that actually aren't counted as being approved. """
        self.assertEqual(choices.InvoiceApproval.not_approved_choices(), ['not_approved'])


@ddt.ddt
class InvoiceNumberingSchemeTestCase(TestCase):
    """ Test cases for `choices.InvoiceNumberingScheme`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Setup test objects. """
        super().setUp()

    def test_default_default(self):
        """ The default value of the `default` choice corresponds to the correct year and month. """
        self.assertEqual(choices.InvoiceNumberingScheme.default_default(), '2018-01')

    def test_default_number(self):
        """ The default value of the `number` choice corresponds to the correct integer. """
        self.assertEqual(choices.InvoiceNumberingScheme.default_number(), '1')

    def test_default_year_month_number(self):
        """ The default value of the `year_month_number` choice corresponds to the correct year, month,
        and number combo. """
        self.assertEqual(choices.InvoiceNumberingScheme.default_year_month_number(), '2018-01-1')

    def test_default_opencraft_year_month(self):
        """ The default value of the `opencraft_year_month` choice corresponds to the correct prefix and
        year, month combo. """
        self.assertEqual(choices.InvoiceNumberingScheme.default_opencraft_year_month(), 'OC-2018-01')

    def test_default_opencraft_number(self):
        """ The default value of the `opencraft_number` choice corresponds to the correct prefix and number combo. """
        self.assertEqual(choices.InvoiceNumberingScheme.default_opencraft_number(), 'OC-1')

    @ddt.data(
        (choices.InvoiceNumberingScheme.default, '2018-01'),
        (choices.InvoiceNumberingScheme.number, '1'),
        (choices.InvoiceNumberingScheme.year_month_number, '2018-01-1'),
        (choices.InvoiceNumberingScheme.opencraft_year_month, 'OC-2018-01'),
        (choices.InvoiceNumberingScheme.opencraft_number, 'OC-1'),
    )
    @ddt.unpack
    def test_default_value(self, numbering_scheme, default_value):
        """ Get the default value of an arbitrary numbering scheme. """
        self.assertEqual(choices.InvoiceNumberingScheme.default_value(numbering_scheme), default_value)

    @ddt.data(
        ('2018-01', '2018-02'),
        ('2018-12', '2019-01'),
    )
    @ddt.unpack
    def test_increment_default(self, value, incremented_value):
        """ Incrementing the `default` choice gives the correct year and month, including for wrap-arounds. """
        self.assertEqual(choices.InvoiceNumberingScheme.increment_default(value), incremented_value)

    @ddt.data(
        ('3', '4'),
        ('000003', '4'),
    )
    @ddt.unpack
    def test_increment_number(self, value, incremented_value):
        """ Incrementing the `number` choice gives the correct number, including with leading 0s. """
        self.assertEqual(choices.InvoiceNumberingScheme.increment_number(value), incremented_value)

    @ddt.data(
        ('2018-01-4', '2018-02-5'),
        ('2018-12-10', '2019-01-11'),
        ('2018-12-0001', '2019-01-2'),
        ('2018-05-37', '2018-06-38'),
        ('2018-05-257', '2018-06-258'),
    )
    @ddt.unpack
    def test_increment_year_month_number(self, value, incremented_value):
        """ Incrementing the `year_month_number` choice gives the correct year, month, and number combo,
         including for wrap-arounds and with leading 0s. """
        self.assertEqual(choices.InvoiceNumberingScheme.increment_year_month_number(value), incremented_value)

    @ddt.data(
        ('OC-2018-01', 'OC-2018-02'),
        ('OC-2018-12', 'OC-2019-01'),
    )
    @ddt.unpack
    def test_increment_opencraft_year_month(self, value, incremented_value):
        """ Incrementing the `opencraft_year_month` choice gives the correct prefix and year, month combo,
         including for wrap-arounds. """
        self.assertEqual(choices.InvoiceNumberingScheme.increment_opencraft_year_month(value), incremented_value)

    @ddt.data(
        ('OC-3', 'OC-4'),
        ('OC-000003', 'OC-4'),
    )
    @ddt.unpack
    def test_increment_opencraft_number(self, value, incremented_value):
        """ Incrementing the `opencraft_number` choice gives the correct prefix and number including for leading 0s. """
        self.assertEqual(choices.InvoiceNumberingScheme.increment_opencraft_number(value), incremented_value)

    @ddt.data(
        (choices.InvoiceNumberingScheme.default, '2018-12', '2019-01'),
        (choices.InvoiceNumberingScheme.number, '2', '3'),
        (choices.InvoiceNumberingScheme.year_month_number, '2018-12-3', '2019-01-4'),
        (choices.InvoiceNumberingScheme.opencraft_year_month, 'OC-2018-09', 'OC-2018-10'),
        (choices.InvoiceNumberingScheme.opencraft_number, 'OC-0002', 'OC-3'),
    )
    @ddt.unpack
    def test_increment_value(self, numbering_scheme, value, incremented_value):
        """ Incrementing an arbitrary numbering scheme always gives the correct incremented value,
        including for values of None. """
        self.assertEqual(choices.InvoiceNumberingScheme.increment_value(numbering_scheme, value), incremented_value)
