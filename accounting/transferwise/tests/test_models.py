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
# pylint: disable=attribute-defined-outside-init

"""
Tests for TransferWise models.
"""

import datetime

from django.utils import timezone
import ddt
import freezegun

from accounting.account.tests.factories import AccountFactory, HourlyRateFactory
from accounting.bank.tests.factories import BankAccountFactory
from accounting.common.tests.base import TestCase
from accounting.invoice.tests.factories import InvoiceFactory
from accounting.transferwise import models
from accounting.transferwise.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


@ddt.ddt
class TransferWiseBulkPaymentTestCase(TestCase):
    """ Test cases for `models.TransferWiseBulkPayment`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.sender = AccountFactory(business_name='OpenCraft GmbH', user__username='opencraft')
        self.bulk_payment = factories.TransferWiseBulkPaymentFactory(date=NOW)
        super().setUp()

    def _create_recipients(self, create_invoices=False, invoice_date=NOW):
        """
        Create recipients for this bulk transfer, and optionally their invoices.

        :param invoices: Whether to create invoices for the recipients.
        :param invoice_date: What date to use for recipient invoices. Defaults to a frozen date.
        :return: The list of recipient accounts that were created.
        """
        self.provider_bank_account1 = BankAccountFactory(transferwise_recipient_id=1)
        self.provider_bank_account2 = BankAccountFactory(transferwise_recipient_id=2)
        HourlyRateFactory(client=self.sender, provider=self.provider_bank_account1.user_account)
        HourlyRateFactory(client=self.sender, provider=self.provider_bank_account2.user_account)
        if create_invoices:
            self.invoice1 = InvoiceFactory(
                date=invoice_date,
                client=self.sender,
                provider=self.provider_bank_account1.user_account
            )
            self.invoice2 = InvoiceFactory(
                date=invoice_date,
                client=self.sender,
                provider=self.provider_bank_account2.user_account
            )
        return [self.provider_bank_account1.user_account, self.provider_bank_account2.user_account]

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(conversion_method(self.bulk_payment), '2018-01-10 20:31:03.350993+00:00: OpenCraft GmbH')

    @ddt.data(NOW, NOW - timezone.timedelta(days=31))
    def test_create_payments(self, date):
        """ Payments are automatically created for all of this bulk payment's recipients. """
        self._create_recipients(create_invoices=True, invoice_date=date)
        self.bulk_payment.create_payments()
        self.assertEqual(models.TransferWisePayment.objects.all().count(), 2)
        self.invoice1.refresh_from_db()
        self.invoice2.refresh_from_db()
        self.assertTrue(self.invoice1.paid)
        self.assertTrue(self.invoice2.paid)

    def test_create_payments_out_of_date_range(self):
        """ Payments are not created because no invoice exists in the date range for this bulk payment. """
        self._create_recipients(create_invoices=True, invoice_date=NOW + timezone.timedelta(days=1))
        self.bulk_payment.create_payments()
        self.assertFalse(models.TransferWisePayment.objects.all().exists())
        self.assertFalse(self.invoice1.paid)
        self.assertFalse(self.invoice2.paid)

    def test_create_payments_all_already_paid(self):
        """ Payments are not created because no invoice exists that's not paid. """
        self._create_recipients(create_invoices=True)
        self.invoice1.paid = True
        self.invoice2.paid = True
        self.invoice1.save()
        self.invoice2.save()
        self.bulk_payment.create_payments()
        self.assertFalse(models.TransferWisePayment.objects.all().exists())
        self.assertTrue(self.invoice1.paid)
        self.assertTrue(self.invoice2.paid)

    def test_create_payments_no_invoice(self):
        """ Payments are not created because an invoice does not exist for the recipients. """
        self._create_recipients()
        self.bulk_payment.create_payments()
        self.assertFalse(models.TransferWisePayment.objects.all().exists())

    def test_csv_filename(self):
        """ The CSV filename contains the proper sender and date. """
        self.assertEqual(self.bulk_payment.csv_filename, 'transferwise_bulk_payment_csv_opencraft_2018-01-10.csv')


@ddt.ddt
class TransferWisePaymentTestCase(TestCase):
    """ Test cases for `models.TransferWisePayment`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Setup test objects. """
        self.provider = AccountFactory(business_name='Developer')
        self.client = AccountFactory(business_name='OpenCraft GmbH')
        self.invoice = InvoiceFactory(provider=self.provider, client=self.client)
        self.payment = factories.TransferWisePaymentFactory(date=NOW, invoice=self.invoice)
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, conversion_method):
        """ String conversion works for both `str` and `repr`. """
        self.assertEqual(
            conversion_method(self.payment),
            '2018-01-10 20:31:03.350993+00:00: OpenCraft GmbH paid Developer'
        )
