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
Tests for Bank models.
"""

import uuid

import ddt

from accounting.account.tests.factories import AccountFactory
from accounting.bank.tests import factories
from accounting.common.tests.base import TestCase


@ddt.ddt
class BankTestCase(TestCase):
    """ Test cases for `models.Bank`. """

    def setUp(self):
        """ Set up test objects. """
        self.uuid = uuid.uuid4()
        self.bank = factories.BankFactory(uuid=self.uuid, name='Bank Name')
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.bank), 'Bank Name - {uuid}'.format(uuid=self.uuid))


@ddt.ddt
class BankAccountTestCase(TestCase):
    """ Test cases for `models.BankAccount`. """

    def setUp(self):
        """ Set up test objects. """
        self.bank = factories.BankFactory(name='Bank Name')
        self.bank_account_holder = AccountFactory(business_name='OpenCraft GmbH', user__username='opencraft')
        self.bank_account = factories.BankAccountFactory(
            bank=self.bank,
            user_account=self.bank_account_holder,
            type=factories.BankAccountType.CHECKING
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.bank_account), 'OpenCraft GmbH: Bank Name (checking)')

    @ddt.data(
        (
            {
                'bic_swift': '',
                'account_number': '',
                'currency': '',
            },
            (),
        ),
        (
            {
                'bic_swift': 'asdf',
                'account_number': 'asdf2',
                'currency': '',
            },
            (
                ('BIC/SWIFT', 'asdf'),
                ('Account Number', 'asdf2'),
            ),
        ),
        (
            {
                'bic_swift': 'asdf',
                'account_number': 'asdf2',
                'currency': 'asdf3',
                'not_a_real_choice': 'asdf4',
            },
            (
                ('BIC/SWIFT', 'asdf'),
                ('Account Number', 'asdf2'),
                ('Currency', 'asdf3'),
            ),
        ),
    )
    @ddt.unpack
    def test_existing_identification(self, identification, expected_output):
        """ The `existing_identification` function returns only what's available. """
        self.bank_account.identification = identification
        self.assertEqual(self.bank_account.existing_identification(), expected_output)
