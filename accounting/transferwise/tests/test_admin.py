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
Tests for the TransferWise admin.
"""

from django.contrib.admin import sites
import ddt

from accounting.common.tests.base import ApiTestCase
from accounting.transferwise import admin, models
from accounting.transferwise.tests import factories


@ddt.ddt
class TransferWiseBulkPaymentAdminTestCase(ApiTestCase):
    """ Test cases for `admin.TransferWiseBulkPaymentAdmin`. """

    def setUp(self):
        """ Set up test objects. """
        self.site = sites.AdminSite()
        self.admin = admin.TransferWiseBulkPaymentAdmin(models.TransferWiseBulkPayment, self.site)
        self.bulk_payment1 = factories.TransferWiseBulkPaymentFactory(csv_path='https://drive.google.com/f/asdf1.csv')
        self.bulk_payment2 = factories.TransferWiseBulkPaymentFactory(csv_path='')
        super().setUp()

    @ddt.data(
        ('bulk_payment1', '<a href="https://drive.google.com/f/asdf1.csv">Click here to see CSV.</a>'),
        ('bulk_payment2', 'No CSV available.'),
    )
    @ddt.unpack
    def test_csv_link(self, bulk_payment, expected_csv_link):
        """The CSV link returns the appropriate HTML and URL."""
        self.assertEqual(self.admin.csv_link(getattr(self, bulk_payment)), expected_csv_link)
