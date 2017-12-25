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

from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from accounting.account.models import Account, Address
from accounting.bank.choices import BankAccountIdentifiers, BankAccountType
from accounting.bank.utils import identification_schema
from accounting.common.models import CommonModel, UuidModel


class Bank(CommonModel, UuidModel):
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


class BankAccount(CommonModel, UuidModel):
    """
    A bank account stores details to help identify a particular user's bank account anywhere in the world.

    Multiple bank accounts can belong to a single user account.

    Because bank account identifiers differ from country to country (although we're moving towards standardizing
    on IBAN & SWIFT/BIC), we let all bank account identifying details be optional, to let the user pick and choose
    what makes sense for their case.

    If in a new political future the world standardizes on IBAN & SWIFT/BIC, we can remove the other fields :)

    The bank account's currency and address, however, always exists, so that is required.
    """

    bank = models.ForeignKey(
        Bank, models.CASCADE, related_name='bank_accounts',
        help_text=_("The bank to which this bank account belongs."))
    user_account = models.ForeignKey(
        Account, models.CASCADE, related_name='bank_accounts',
        help_text=_("The user account that this bank account is linked to. "
                    "A user can have multiple bank accounts associated with their user account."))
    type = models.CharField(
        max_length=30, choices=BankAccountType.choices,
        help_text=_("Whether this is a checking or savings account."))
    transferwise_recipient_id = models.IntegerField(
        blank=True, null=True,
        help_text=_("The TransferWise recipient ID used to identify recipient accounts which contain "
                    "bank account information."))
    identification = JSONField(
        blank=True, default=identification_schema,
        help_text=_("Unique identification information for this bank account."))

    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')

    def __str__(self):
        """
        Indicate who this bank account belongs to and in which bank it is.
        """
        return '{username}: {bank_name} ({type})'.format(
            username=self.user_account,
            bank_name=self.bank.name,
            type=self.type,
        )

    def existing_identification(self):
        """
        Get only the bank account identification details that exist.
        """
        return tuple(
            (name, self.identification[key])  # pylint: disable=unsubscriptable-object
            for key, name in BankAccountIdentifiers.choices
            if self.identification[key]  # pylint: disable=unsubscriptable-object
        )
