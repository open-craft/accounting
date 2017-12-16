# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2017 OpenCraft <contact@opencraft.com>
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

from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import CurrencyField
from localflavor.au.models import AUBusinessNumberField
from localflavor.generic.models import BICField, IBANField
from vies.models import VATINField

from accounting.account.models import Account, Address
from accounting.bank.fields import AUBankStateBranchField


class Bank(models.Model):
    """
    A bank to represent more details about bank accounts for users.
    """

    uuid = models.UUIDField(
        blank=False, null=False, default=uuid4, editable=False, verbose_name=_("UUID"),
        help_text=_("The universally unique identifier for this bank."))
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


class BankAccount(models.Model):
    """
    A bank account stores details to help identify a particular user's bank account anywhere in the world.

    Multiple bank accounts can belong to a single user account.

    Because bank account identifiers differ from country to country (although we're moving towards standardizing
    on IBAN & SWIFT/BIC), we let all bank account identifying details be optional, to let the user pick and choose
    what makes sense for their case.

    If in a new political future the world standardizes on IBAN & SWIFT/BIC, we can remove the other fields :)

    The bank account's currency and address, however, always exists, so that is required.
    """

    CHECKING = 'checking'
    SAVINGS = 'savings'
    BANK_ACCOUNT_TYPES = (
        (CHECKING, _("Checking Account")),
        (SAVINGS, _("Savings Account")),
    )

    uuid = models.UUIDField(
        blank=False, null=False, default=uuid4, editable=False, verbose_name=_("UUID"),
        help_text=_("The universally unique identifier for this bank account."))
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
        max_length=30, choices=BANK_ACCOUNT_TYPES,
        help_text=_("Whether this is a checking or savings account."))
    iban = IBANField(
        blank=True, null=True,
        help_text=_("The unique International Bank Account Number of the provider's bank account."))
    bic = BICField(
        blank=True, null=True,
        help_text=_("The 11-character SWIFT / BIC (Business Identifier Code) code used to identify a "
                    "bank or financial institution globally."))
    abn = AUBusinessNumberField(
        blank=True, null=True,
        help_text=_("The 11-character Australian Business Number used to identify business entities in Australia."))
    bsb = AUBankStateBranchField(
        blank=True, null=True,
        help_text=_("The 6-character Bank State Branch code used as a bank identifier in Australia."))
    vat = VATINField(
        blank=True, null=True,
        help_text=_("The Value Added Tax identification number used in and required by some countries. "
                    "This can also be used to store a General Sales Tax (GST) identification number."))
    account_number = models.CharField(
        max_length=30, blank=True, null=True,
        help_text=_("The bank account number used to help identify the account. "
                    "Required for only some countries."))
    routing_number = models.CharField(
        max_length=30, blank=True, null=True,
        help_text=_("The bank account routing number used to help identify the account. "
                    "Required for only some countries."))

    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')

    def __str__(self):
        """
        Indicate who this bank account belongs to and in which bank it is.
        """
        return '{username}: {bank_name} ({currency}, {type})'.format(
            username=str(self.user_account),
            bank_name=self.bank.name,
            currency=self.currency,
            type=self.type,
        )
