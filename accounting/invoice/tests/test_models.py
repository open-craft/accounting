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
Tests for Invoice models.
"""

import datetime

from django.utils import timezone
import ddt
import freezegun

from accounting.account.tests.factories import AccountFactory
from accounting.common.tests.base import TestCase
from accounting.invoice.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


@ddt.ddt
class InvoiceTemplateTestCase(TestCase):
    """ Test cases for `models.InvoiceTemplate`. """

    def setUp(self):
        """ Set up test objects. """
        self.provider = AccountFactory(business_name='Developer', user__username='developer')
        self.invoice_template = factories.InvoiceTemplateFactory(provider=self.provider)
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.invoice_template), "Developer's Invoice Template")


@ddt.ddt
class InvoiceTestCase(TestCase):
    """ Test cases for `models.Invoice`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.provider = AccountFactory(business_name='Developer', user__username='developer')
        self.client = AccountFactory(business_name='OpenCraft GmbH', user__username='opencraft')
        self.invoice = factories.InvoiceFactory(provider=self.provider, client=self.client, date=NOW)
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(
            conversion_method(self.invoice),
            '2018-01-10: Developer invoicing OpenCraft GmbH (PENDING)'
        )


@ddt.ddt
class LineItemTestCase(TestCase):
    """ Test cases for `models.LineItem`. """

    def setUp(self):
        """ Set up test objects. """
        self.line_item = factories.LineItemFactory(
            line_item_id=1,
            key='OC-4000',
            name='Accounting: Refactor bad test code from OC-3589',
            quantity=2,
            price__amount=100,
            price__currency='EUR'
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(
            conversion_method(self.line_item),
            '(1) OC-4000 - Accounting: Refactor bad test code from OC-3589 (2 x 100.00 EUR = 200.00 EUR)'
        )
