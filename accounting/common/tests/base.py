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
Base classes for test classes throughout the Accounting service.
"""

from django.contrib.sites.models import Site
from django.test import TestCase as DjangoTestCase

from accounting.account.tests.factories import AccountFactory, HourlyRateFactory
from accounting.invoice.models import Invoice


class TestCase(DjangoTestCase):
    """ Common test case for test classes throughout the Accounting service. """

    def setUp(self):
        """ Set up test objects. """
        Site.objects.all().delete()
        Site.objects.create(id=1, domain='https://billing.opencraft.com')
        super().setUp()

    def tearDown(self):
        """ Delete any leftover files. """
        for invoice in Invoice.objects.all():
            invoice.extra_image.delete()
        super().tearDown()

    def create_client_and_provider_links(self):
        """ Create a client and some providers, and link them with hourly rates. """
        # pylint: disable=attribute-defined-outside-init
        self.client = AccountFactory(
            business_name='OpenCraft GmbH',
            user__username='opencraft',
            user__email='billing@opencraft.com'
        )
        self.provider1 = AccountFactory()
        self.provider2 = AccountFactory()
        HourlyRateFactory(client=self.client, provider=self.provider1)
        HourlyRateFactory(client=self.client, provider=self.provider2)
