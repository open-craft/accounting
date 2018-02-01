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
Invoice tasks tests.
"""

from unittest import mock
import datetime

from django.core import mail
from django.core.mail.message import EmailMessage
from django.utils import timezone
import ddt
import freezegun

from accounting.common.tests.base import TestCase
from accounting.invoice import choices, models, tasks
from accounting.invoice.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)
PAST = NOW - datetime.timedelta(days=NOW.day)


@ddt.ddt
class InvoicePreparationNotificationTestCase(TestCase):
    """ Test cases for `tasks.send_invoice_prep_notification`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.create_client_and_provider_links()
        super().setUp()

    @freezegun.freeze_time(NOW)
    def test_send_invoice_prep_notification(self):
        """ The invoice preparation notification email sent out every month contains proper information. """
        tasks.send_invoice_prep_notification()
        # Only a single email is sent out per client, with all providers in the BCC list.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].bcc, [self.provider1.user.email, self.provider2.user.email])
        self.assertEqual(mail.outbox[0].to, [])
        self.assertEqual(mail.outbox[0].cc, [self.client.user.email])
        self.assertEqual(mail.outbox[0].subject, 'Preparing your invoice for December')
        self.assertEqual(mail.outbox[0].body, (
            "Hello,\n"
            "\n"
            "At the beginning of each month, to help you gain time in invoicing your hours, "
            "I automatically build an invoice based on the worklogs you logged in Jira the month before.\n"
            "\n"
            "I just wanted to let you know that I'll be doing this soon -- I'll send you an invoice "
            "for December to approve on January 3rd.\n"
            "\n"
            "Could you review your worklogs in Jira to ensure that they are accurate, before that date?\n"
            "\n"
            "Thank you!\n"
        ))


@ddt.ddt
class InvoiceApprovalRequestTestCase(TestCase):
    """ Test cases for `tasks.send_invoice_approval_request`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.create_client_and_provider_links()

        # Create invoices that are from the past. The task will use these to make new ones.
        self.template1 = factories.InvoiceTemplateFactory(provider=self.provider1)
        self.template2 = factories.InvoiceTemplateFactory(provider=self.provider2)
        self.old_invoice1 = factories.InvoiceFactory(
            date=PAST, provider=self.provider1, client=self.client, template=self.template1)
        self.old_invoice2 = factories.InvoiceFactory(
            date=PAST, provider=self.provider2, client=self.client, template=self.template2)
        super().setUp()

    @freezegun.freeze_time(NOW)
    @mock.patch.object(models.Invoice, 'upload_to_google_drive')
    @mock.patch.object(models.Invoice, 'fill_line_items_from_jira')
    @mock.patch.object(EmailMessage, 'attach_file')
    @mock.patch.object(models.Invoice, 'to_pdf')
    def test_send_invoice_approval_request(self, mock_to_pdf, mock_attach_file, mock_fill_line_items_from_jira,
                                           mock_upload_to_google_drive):
        """ The invoice approval request email sent out every month contains proper information. """
        # Mock.
        pdf_path = 'https://drive.google.com/invoice.pdf'
        mock_upload_to_google_drive.return_value = {'alternateLink': pdf_path}
        mock_to_pdf.return_value = pdf_path

        # Call.
        tasks.send_invoice_approval_request()

        # 2 providers, so 2 of everything.
        self.assertEqual(mock_to_pdf.call_count, 2)
        self.assertEqual(mock_attach_file.call_count, 2)
        self.assertEqual(mock_fill_line_items_from_jira.call_count, 2)
        self.assertEqual(mock_upload_to_google_drive.call_count, 2)
        self.assertEqual(len(mail.outbox), 2)

        # Email subjects should be the same.
        self.assertEqual(mail.outbox[0].subject, mail.outbox[1].subject)
        self.assertEqual(mail.outbox[0].subject, 'Approve your invoice for December')

        # Body contains proper invoice approval URL and text, for both providers.
        body = (
            "Hello,\n"
            "\n"
            "I have prepared your invoice for December! It is attached and ready for you to review.\n"
            "\n"
            "When you've looked it over, can you approve it by clicking on this link, "
            "or by visiting it in your browser?\n"
            "\n"
            "https://billing.opencraft.com/invoice/{uuid}/approve/\n"
            "\n"
            "If you find any issues with your invoice, please contact billing@opencraft.com before January 5th -- "
            "I will consider your invoice approved by then, and will proceed to sending the corresponding payment.\n"
        )
        invoices = models.Invoice.objects.filter(date__month=NOW.month)
        self.assertEqual(mail.outbox[0].body, body.format(uuid=invoices.first().uuid))
        self.assertEqual(mail.outbox[1].body, body.format(uuid=invoices.last().uuid))


@ddt.ddt
class InvoiceFinalizationTestCase(TestCase):
    """ Test cases for `tasks.send_final_invoices`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.create_client_and_provider_links()

        # Create invoices for the month. The task will consider these the final ones.
        self.invoice1 = factories.InvoiceFactory(date=NOW, provider=self.provider1, client=self.client)
        self.invoice2 = factories.InvoiceFactory(date=NOW, provider=self.provider2, client=self.client)
        super().setUp()

    @freezegun.freeze_time(NOW)
    @mock.patch.object(models.Invoice, 'upload_to_google_drive')
    @mock.patch.object(models.Invoice, 'fill_line_items_from_jira')
    @mock.patch.object(EmailMessage, 'attach_file')
    @mock.patch.object(models.Invoice, 'to_pdf')
    def test_send_final_invoices(self, mock_to_pdf, mock_attach_file, mock_fill_line_items_from_jira,
                                 mock_upload_to_google_drive):
        """ The invoice finalization email sent out every month contains proper information. """
        # Mock.
        pdf_path = 'https://drive.google.com/invoice.pdf'
        mock_upload_to_google_drive.return_value = {'alternateLink': pdf_path}
        mock_to_pdf.return_value = pdf_path

        # Call.
        tasks.send_final_invoices()
        self.invoice1.refresh_from_db()
        self.invoice2.refresh_from_db()

        # The invoices will be marked as automatically approved since nobody visited the URL.
        self.assertTrue(self.invoice1.is_approved)
        self.assertTrue(self.invoice2.is_approved)
        self.assertEqual(self.invoice1.approved, choices.InvoiceApproval.automatically)
        self.assertEqual(self.invoice2.approved, choices.InvoiceApproval.automatically)

        # 2 providers, so 2 of everything.
        self.assertEqual(models.Invoice.objects.all().count(), 2)
        self.assertEqual(mock_to_pdf.call_count, 2)
        self.assertEqual(mock_attach_file.call_count, 2)
        mock_fill_line_items_from_jira.assert_not_called()
        self.assertEqual(mock_upload_to_google_drive.call_count, 2)
        self.assertEqual(len(mail.outbox), 2)

        # Email subjects should be the same.
        self.assertEqual(mail.outbox[0].subject, mail.outbox[1].subject)
        self.assertEqual(mail.outbox[0].subject, 'Your approved invoice for December')

        # Body contains proper invoice approval URL and text, for both providers.
        body = (
            "Hello,\n"
            "\n"
            "I have attached your finalized and approved invoice for December.\n"
            "\n"
            "We are now proceeding to send the bank transfers, and you can expect payment to arrive "
            "in your bank account within 5-8 business days at most.\n"
            "\n"
            "If you have any issues, please contact billing@opencraft.com.\n"
        )
        self.assertEqual(mail.outbox[0].body, body.format(self.invoice1.uuid))
        self.assertEqual(mail.outbox[1].body, body.format(self.invoice2.uuid))
