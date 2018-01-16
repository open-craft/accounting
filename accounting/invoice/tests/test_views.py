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
Tests for Invoice views.
"""

import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
import freezegun

from accounting.account.tests.factories import AccountFactory
from accounting.authentication.tests.factories import UserFactory
from accounting.invoice import choices
from accounting.invoice.tests import factories

NOW = datetime.datetime(2018, 1, 10, 20, 31, 3, 350993, tzinfo=timezone.utc)


class InvoiceViewSetTestCase(APITestCase):
    """ Test cases for `views.InvoiceViewSet`. """

    @freezegun.freeze_time(NOW)
    def setUp(self):
        """ Set up test objects. """
        self.admin = UserFactory(is_staff=True)
        self.provider_account = AccountFactory(business_name='Developer', user__username='developer')
        self.client_account = AccountFactory(business_name='OpenCraft GmbH', user__username='opencraft')
        self.invoice = factories.InvoiceFactory(provider=self.provider_account, client=self.client_account, date=NOW)
        super().setUp()

    def test_approve(self):
        """ Approving an invoice through the appropriate URL is considered manual approval. """
        # First visit approves the invoice.
        url = reverse('invoice:invoice-approve', [self.invoice.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'approved': True})
        self.invoice.refresh_from_db()
        self.assertTrue(self.invoice.is_approved)
        self.assertEqual(self.invoice.approved, choices.InvoiceApproval.manually)

        # Second visit when already approved doesn't change anything.
        url = reverse('invoice:invoice-approve', [self.invoice.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})
        self.invoice.refresh_from_db()
        self.assertTrue(self.invoice.is_approved)
        self.assertEqual(self.invoice.approved, choices.InvoiceApproval.manually)

    def test_pay(self):
        """ Paying an invoice through the appropriate URL marks the invoice as paid. """
        self.client.force_authenticate(user=self.admin)

        # First visit pays the invoice.
        url = reverse('invoice:invoice-pay', [self.invoice.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('paid'))
        self.invoice.refresh_from_db()
        self.assertTrue(self.invoice.paid)

        # Second visit when already paid doesn't change anything.
        url = reverse('invoice:invoice-pay', [self.invoice.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})
        self.invoice.refresh_from_db()
        self.assertTrue(self.invoice.paid)
