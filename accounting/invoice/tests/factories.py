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
Factories for testing the Invoice application.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from factory import fuzzy
import factory

from accounting.account.tests.factories import AccountFactory, HourlyRateFactory, MoneyFactory
from accounting.common.tests.factories import UuidFactory
from accounting.invoice import models


class InvoiceFactory(UuidFactory):
    """ Factory for `models.Invoice`. """

    provider = factory.SubFactory(AccountFactory)
    client = factory.SubFactory(AccountFactory)
    extra_text = factory.Faker('text')
    extra_image = factory.django.ImageField()
    pdf_path = factory.Faker('uri')

    class Meta:
        model = models.Invoice

    @factory.post_generation
    def set_hourly_rate(self, create, extracted, **kwargs):
        """
        Set an hourly rate between the provider and client.
        """
        try:
            HourlyRateFactory(client=self.client, provider=self.provider, hourly_rate__currency='EUR')
        except (IntegrityError, ValidationError):
            pass


class LineItemFactory(factory.DjangoModelFactory):
    """ Factory for `models.LineItem`. """

    invoice = factory.SubFactory(InvoiceFactory)
    line_item_id = fuzzy.FuzzyInteger(-999999, high=+999999)
    key = fuzzy.FuzzyText()
    name = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()
    quantity = fuzzy.FuzzyDecimal(1, high=100, precision=8)
    price = factory.SubFactory(MoneyFactory)

    class Meta:
        model = models.LineItem
