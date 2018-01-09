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
Factories for testing the TransferWise application.
"""

import factory

from accounting.account.tests.factories import AccountFactory
from accounting.common.tests.factories import UuidFactory
from accounting.invoice.tests.factories import InvoiceFactory
from accounting.transferwise import models


class TransferWiseBulkPaymentFactory(UuidFactory):
    """ Factory for `models.TransferWiseBulkPayment`. """

    sender = factory.SubFactory(AccountFactory)
    csv_path = factory.Faker('uri')

    class Meta:
        model = models.TransferWiseBulkPayment


class TransferWisePaymentFactory(UuidFactory):
    """ Factory for `models.TransferWisePayment`. """

    bulk_payment = factory.SubFactory(TransferWiseBulkPaymentFactory)
    invoice = factory.SubFactory(InvoiceFactory)

    class Meta:
        model = models.TransferWisePayment
