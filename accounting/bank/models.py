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
Bank application models.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields.json import JSONField
from djmoney.models.fields import CurrencyField

from accounting.account.models import Account, Address
from accounting.bank.choices import BankAccountIdentifiers, BankAccountType
from accounting.common.models import UuidModel


class Bank(UuidModel):
    """
    A bank to represent more details about bank accounts for users.
    """

    name = models.CharField(
        max_length=80,
        help_text=_("The official name of the bank."))
    address = models.ForeignKey(
        Address, models.CASCADE, related_name='banks', blank=True, null=True,
        help_text=_("The address of this bank."))

    class Meta:
        verbose_name = _('Bank')
        verbose_name_plural = _('Banks')

    def __str__(self):
        """
        Identify the bank by name and UUID.
        """
        return '{name} - {identifier}'.format(name=self.name, identifier=self.uuid)


class BankAccount(UuidModel):
    """
    A bank account stores details to help identify a particular user's bank account anywhere in the world.

    Multiple bank accounts can belong to a single user account.

    Because bank account identifiers differ from country to country (although we're moving towards standardizing
    on IBAN & SWIFT/BIC), we let all bank account identifying details be optional, to let the user pick and choose
    what makes sense for their case.

    If in a new political future the world standardizes on IBAN & SWIFT/BIC, we can remove the other fields :)

    The bank account's currency and address, however, always exists, so that is required.
    """

    IDENTIFICATION_SCHEMA = {identifier[0]: '' for identifier in BankAccountIdentifiers.choices}

    bank = models.ForeignKey(
        Bank, models.CASCADE, related_name='bank_accounts',
        help_text=_("The bank to which this bank account belongs."))
    user_account = models.ForeignKey(
        Account, models.CASCADE, related_name='bank_accounts',
        help_text=_("The user account that this bank account is linked to. "
                    "A user can have multiple bank accounts associated with their user account."))
    currency = CurrencyField(
        help_text=_("The currency expected to be held in this bank account."))
    type = models.CharField(
        max_length=30, choices=BankAccountType.choices,
        help_text=_("Whether this is a checking or savings account."))
    identification = JSONField(
        blank=True, default=IDENTIFICATION_SCHEMA,
        help_text=_("The unique combination of identification information for this bank account."))

    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')

    def __str__(self):
        """
        Indicate who this bank account belongs to and in which bank it is.
        """
        return '{username}: {bank_name} ({currency}, {type})'.format(
            username=self.user_account,
            bank_name=self.bank.name,
            currency=self.currency,
            type=self.type,
        )
