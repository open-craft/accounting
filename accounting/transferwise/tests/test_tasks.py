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
TransferWise tasks tests.
"""

from unittest import mock
import datetime

from django.core import mail
from django.core.mail.message import EmailMessage
from django.utils import timezone
import ddt
import freezegun

from accounting.bank.tests.factories import BankAccountFactory
from accounting.common.tests.base import TestCase
from accounting.transferwise import models, tasks
from accounting.transferwise.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)
PAST = NOW - datetime.timedelta(days=NOW.day)


@ddt.ddt
class SendBulkPaymentCsvTestCase(TestCase):
    """ Test cases for `tasks.send_bulk_payment_csv`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.create_client_and_provider_links()

        # The providers need valid bank accounts to get paid.
        self.bank_account1 = BankAccountFactory(user_account=self.provider1)
        self.bank_account2 = BankAccountFactory(user_account=self.provider2)

        # Create some unpaid invoices that need to be paid in bulk.
        self.invoice1 = factories.InvoiceFactory(provider=self.provider1, client=self.client, paid=False)
        self.invoice2 = factories.InvoiceFactory(provider=self.provider2, client=self.client, paid=False)
        super().setUp()

    @mock.patch.object(models.TransferWiseBulkPayment, 'upload_to_google_drive')
    @mock.patch.object(EmailMessage, 'attach_file')
    @mock.patch.object(models.TransferWiseBulkPayment, 'to_bulk_payment_csv')
    def test_send_bulk_payment_csv(self, mock_to_bulk_payment_csv, mock_attach_file, mock_upload_to_google_drive):
        """ A bulk payment CSV is generated for all upaid invoices, sent of to the bulk payment sender,
        and uploaded to Google Drive. """
        # Mock.
        csv_path = 'https://drive.google.com/bulk_payment.csv'
        mock_upload_to_google_drive.return_value = {'alternateLink': csv_path}
        mock_to_bulk_payment_csv.return_value = mock.MagicMock(name=csv_path)

        # Call.
        tasks.send_bulk_payment_csv()

        # The invoices will be marked as paid.
        self.invoice1.refresh_from_db()
        self.invoice2.refresh_from_db()
        self.assertTrue(self.invoice1.paid)
        self.assertTrue(self.invoice2.paid)

        # 1 sender, so 1 call to everything.
        mock_to_bulk_payment_csv.assert_called_once()
        mock_attach_file.assert_called_once()
        mock_upload_to_google_drive.assert_called_once()
        self.assertEqual(len(mail.outbox), 1)

        # 1 bulk payment that contains 2 payments, 1 for each provider.
        self.assertEqual(models.TransferWiseBulkPayment.objects.count(), 1)
        self.assertEqual(models.TransferWisePayment.objects.count(), 2)
        self.assertEqual(models.TransferWiseBulkPayment.objects.get().payments.count(), 2)

        # Email contains passed in subject and body.
        self.assertEqual(mail.outbox[0].subject, 'TransferWise Bulk Payment CSV')
        self.assertEqual(mail.outbox[0].body, 'TransferWise Bulk Payment CSV is attached.')
