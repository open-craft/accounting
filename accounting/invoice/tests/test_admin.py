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
Tests for the Invoice admin.
"""

import datetime

from django.contrib.admin import ACTION_CHECKBOX_NAME, sites
from django.urls import reverse
from django.utils import timezone
import ddt
import freezegun

from accounting.authentication.tests.factories import UserFactory
from accounting.common.tests.base import ApiTestCase
from accounting.invoice import admin, choices, models
from accounting.invoice.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


@ddt.ddt
class InvoiceAdminTestCase(ApiTestCase):
    """ Test cases for `admin.InvoiceAdmin`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.create_client_and_provider_links()
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.url = reverse('admin:invoice_invoice_changelist')
        self.site = sites.AdminSite()
        self.admin = admin.InvoiceAdmin(models.Invoice, self.site)
        self.invoice1 = factories.InvoiceFactory(
            client=self.client_account,
            provider=self.provider1,
            pdf_path='https://drive.google.com/f/asdf1.pdf',
            paid=True,
            approved=choices.InvoiceApproval.not_approved
        )
        self.invoice2 = factories.InvoiceFactory(
            client=self.client_account,
            provider=self.provider1,
            pdf_path='https://drive.google.com/f/asdf2.pdf',
            paid=False,
            approved=choices.InvoiceApproval.manually
        )
        self.invoice3 = factories.InvoiceFactory(
            client=self.client_account,
            provider=self.provider1,
            pdf_path='',
            paid=False,
            approved=choices.InvoiceApproval.automatically
        )
        # Make line items just for invoice 2 and 3, so invoice 1 has a total of '0.00 EUR'.
        factories.LineItemFactory(invoice=self.invoice2, quantity=1, price__amount=100, price__currency='EUR')
        factories.LineItemFactory(invoice=self.invoice3, quantity=2, price__amount=100, price__currency='EUR')
        super().setUp()

    def _refresh_invoices(self):
        """Refresh the test case's invoices from the database to have the object reflect new updates."""
        for invoice in [self.invoice1, self.invoice2, self.invoice3]:
            invoice.refresh_from_db()

    @ddt.data(
        ('invoice1', '0.00 EUR'),
        ('invoice2', '100.00 EUR'),
        ('invoice3', '200.00 EUR'),
    )
    @ddt.unpack
    def test_total(self, invoice, expected_total):
        """The total is displayed with appropriate cost and currency."""
        self.assertEqual(self.admin.total(getattr(self, invoice)), expected_total)

    @ddt.data(
        ('invoice1', '<a href="https://drive.google.com/f/asdf1.pdf">Click here to see PDF.</a>'),
        ('invoice2', '<a href="https://drive.google.com/f/asdf2.pdf">Click here to see PDF.</a>'),
        ('invoice3', 'No PDF available.'),
    )
    @ddt.unpack
    def test_pdf_link(self, invoice, expected_pdf_link):
        """The PDF link returns the appropriate HTML and URL."""
        self.assertEqual(self.admin.pdf_link(getattr(self, invoice)), expected_pdf_link)

    def test_jira_timesheet_link(self):
        """The JIRA Timesheet link contains the appropriate URL parameters."""
        self.provider1.user.username = 'umanshahzad'
        self.assertEqual(
            self.admin.jira_timesheet_link(self.invoice1),
            '<a href="'
            'https://jira.atlassian.com/secure/TempoUserBoard!timesheet.jspa'
            '?userId=umanshahzad'
            '&amp;periodType=BILLING'
            '&amp;periodView=DATES'
            '&amp;from=2017-12-01'
            '&amp;to=2017-12-31">'
            'Click here to see JIRA worklogs.'
            '</a>'
        )

    def test_mark_paid(self):
        """Marking a set of invoices as paid through the admin should only mark selected invoices as paid."""
        self.client.force_login(self.admin_user)
        self.client.post(self.url, data={
            'action': 'mark_paid',
            ACTION_CHECKBOX_NAME: [self.invoice1.pk, self.invoice2.pk],
        })

        self._refresh_invoices()
        self.assertTrue(self.invoice1.paid)
        self.assertTrue(self.invoice2.paid)
        self.assertFalse(self.invoice3.paid)

    def test_mark_approved(self):
        """Marking a set of invoices as approved through the admin should only mark selected invoices as manually
        approved. Approval status remains the same if already previously approved."""
        # An extra, unapproved invoice to leave out of selection, to ensure it isn't approved after the operation.
        invoice4 = factories.InvoiceFactory(
            client=self.client_account,
            provider=self.provider1,
            pdf_path='https://drive.google.com/f/asdf4.pdf',
            paid=True,
            approved=choices.InvoiceApproval.not_approved
        )
        self.client.force_login(self.admin_user)
        self.client.post(self.url, data={
            'action': 'mark_approved',
            ACTION_CHECKBOX_NAME: [self.invoice1.pk, self.invoice2.pk, self.invoice3.pk],
        })

        self._refresh_invoices()
        invoice4.refresh_from_db()
        self.assertTrue(self.invoice1.is_approved)
        self.assertTrue(self.invoice2.is_approved)
        self.assertTrue(self.invoice3.is_approved)
        self.assertFalse(invoice4.is_approved)
        self.assertEqual(self.invoice1.approved, choices.InvoiceApproval.manually)
        self.assertEqual(self.invoice2.approved, choices.InvoiceApproval.manually)
        self.assertEqual(self.invoice3.approved, choices.InvoiceApproval.automatically)
        self.assertEqual(invoice4.approved, choices.InvoiceApproval.not_approved)
