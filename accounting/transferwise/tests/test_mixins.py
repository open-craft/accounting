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
Tests for TransferWise mixins.
"""

import csv
import datetime
import os

from django.utils import timezone
import freezegun

from accounting.account.tests.factories import AccountFactory
from accounting.bank.tests.factories import BankAccountFactory
from accounting.common.tests.base import TestCase
from accounting.invoice.tests.factories import InvoiceFactory, LineItemFactory
from accounting.transferwise import mixins
from accounting.transferwise.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


class TransferWiseCsvMixinTestCase(TestCase):
    """ Test cases for `mixins.TransferWiseCsvMixin`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.sender = AccountFactory(business_name='OpenCraft GmbH')
        self.payment1 = self._create_payment(recipient_bank_account_kwargs={
            'transferwise_recipient_id': 1,
            'user_account__business_name': 'Developer 1',
            'identification': {
                'account_number': 10,
                'currency': 'PKR',
            }
        })
        self.payment2 = self._create_payment(recipient_bank_account_kwargs={
            'transferwise_recipient_id': 2,
            'user_account__business_name': 'Developer 2',
            'identification': {
                'account_number': 11,
                'currency': 'USD',
            }
        })
        self.mixin = mixins.TransferWiseCsvMixin()
        self.csv_path = ''
        super().setUp()

    def tearDown(self):
        """ Delete any leftover files. """
        if self.csv_path:
            os.unlink(self.csv_path.name)
        super().tearDown()

    def _create_payment(self, recipient_bank_account_kwargs=None):
        """ Create a `TransferWisePayment` and return it. """
        if recipient_bank_account_kwargs is None:
            recipient_bank_account_kwargs = {}
        recipient_bank_account = BankAccountFactory(**recipient_bank_account_kwargs)
        invoice = InvoiceFactory(date=NOW, client=self.sender, provider=recipient_bank_account.user_account)
        LineItemFactory(
            invoice=invoice,
            quantity=1,
            price__amount='100',
            price__currency=recipient_bank_account.identification['currency'] or 'EUR'
        )
        return factories.TransferWisePaymentFactory(invoice=invoice)

    def test_to_bulk_payment_csv(self):
        """ A bulk payment CSV is generated with all the proper columns and rows. """
        self.csv_path = self.mixin.to_bulk_payment_csv([self.payment1, self.payment2])
        with open(self.csv_path.name, newline='') as csv_file:
            reader = csv.reader(csv_file)
            self.assertEqual(next(reader), [
                'recipientId',
                'name',
                'account',
                'sourceCurrency',
                'targetCurrency',
                'amountCurrency',
                'amount',
                'paymentReference'
            ])
            self.assertEqual(next(reader), [
                '1',
                'Developer 1',
                '10',
                'EUR',
                'PKR',
                'EUR',
                '100.0000000000',
                '2018-01'
            ])
            self.assertEqual(next(reader), [
                '2',
                'Developer 2',
                '11',
                'EUR',
                'USD',
                'EUR',
                '100.0000000000',
                '2018-01'
            ])
            with self.assertRaises(StopIteration):
                next(reader)

    def test_to_bulk_payment_csv_no_payments(self):
        """ A bulk payment CSV is generated with only columns and no rows because no payments exist. """
        self.csv_path = self.mixin.to_bulk_payment_csv([])
        with open(self.csv_path.name, newline='') as csv_file:
            reader = csv.reader(csv_file)
            self.assertEqual(next(reader), [
                'recipientId',
                'name',
                'account',
                'sourceCurrency',
                'targetCurrency',
                'amountCurrency',
                'amount',
                'paymentReference'
            ])
            with self.assertRaises(StopIteration):
                next(reader)
