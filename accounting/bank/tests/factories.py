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
Factories for testing the Bank application.
"""

from factory import fuzzy
import factory

from accounting.account.tests.factories import AccountFactory
from accounting.address.tests.factories import AddressFactory
from accounting.bank import models
from accounting.bank.choices import BankAccountType
from accounting.common.tests.factories import UuidFactory


class BankFactory(UuidFactory):
    """ Factory for `models.Bank`. """

    name = factory.Faker('company')
    address = factory.SubFactory(AddressFactory)

    class Meta:
        model = models.Bank


class BankAccountFactory(UuidFactory):
    """ Factory for `models.BankAccount`. """

    bank = factory.SubFactory(BankFactory)
    user_account = factory.SubFactory(AccountFactory)
    type = fuzzy.FuzzyChoice([BankAccountType.CHECKING, BankAccountType.SAVINGS])
    transferwise_recipient_id = fuzzy.FuzzyInteger(1, high=99999)

    class Meta:
        model = models.BankAccount
