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
Factories for testing the Account application.
"""

from uuid import uuid4
import string

from djmoney.money import Money
from factory import fuzzy
from moneyed import CURRENCIES
import factory  # pylint: disable=ungrouped-imports

from accounting.account import models
from accounting.address.tests.factories import AddressFactory
from accounting.authentication.tests.factories import UserFactory


class MoneyFactory(factory.Factory):
    """ Factory for `djmoney.money.Money`. We all wish we had a `MoneyFactory`. """

    amount = fuzzy.FuzzyDecimal(10, high=200)
    currency = fuzzy.FuzzyChoice(CURRENCIES)

    class Meta:
        model = Money


class AccountFactory(factory.DjangoModelFactory):
    """ Factory for `models.Account`. """

    uuid = factory.LazyFunction(uuid4)
    user = factory.SubFactory(UserFactory)
    address = factory.SubFactory(AddressFactory)
    business_name = factory.Faker('company')
    occupation = factory.Faker('job')
    vat = fuzzy.FuzzyText(chars=string.digits)

    class Meta:
        model = models.Account


class HourlyRateFactory(factory.DjangoModelFactory):
    """ Factory for `models.HourlyRate. """

    uuid = factory.LazyFunction(uuid4)
    hourly_rate = factory.SubFactory(MoneyFactory)
    provider = factory.SubFactory(AccountFactory)
    client = factory.SubFactory(AccountFactory)

    class Meta:
        model = models.HourlyRate
