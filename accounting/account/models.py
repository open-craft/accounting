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
Account models used for user accounts in the Accounting service.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField

USER_MODEL = get_user_model()


class Account(models.Model):
    """
    An account contains accounting details for a user, i.e. bank account details.

    A user's accounts can have multiples of certain types of data.
    For example, a user can have multiple bank accounts, multiple addresses, or multiple hourly rates
    which differ per client where the user is the provider.
    """

    user = models.OneToOneField(
        USER_MODEL, models.CASCADE, related_name='account',
        help_text=_("The authentication user linked to this account."))
    address = models.ForeignKey(
        Address, models.CASCADE, related_name='accounts',
        help_text=_("The address of this user."))
    business_name = models.CharField(
        max_length=120, blank=True, null=True,
        help_text=_("The name of the business or company associated with this account."))
    occupation = models.CharField(
        max_length=80, blank=True, null=True,
        help_text=_("The occupation of the user of this account. "
                    "Required if country is US, CA, or JP."))

    # We link hourly rates to other accounts, because an account can exist for both a provider and a client, and
    # because hourly rates can differ for a provider per client, and vice versa. For example:
    #     - Provider A has a X EUR/hour rate for Client F.
    #     - Provider A has a Y EUR/hour rate for Client G.
    #     - Client F pays X EUR/hour for Provider A.
    #     - Client F pays Z EUR/hour for Provider B.
    # For technical details, see
    # https://docs.djangoproject.com/en/2.0/topics/db/models/#extra-fields-on-many-to-many-relationships
    hourly_rate = models.ManyToManyField(
        'self', through='HourlyRate', symmetrical=False,
        help_text=_("The hourly rate the user charges clients."))

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    def __str__(self):
        """
        Returns a string indicating to whom this account belongs.
        """
        return self.business_name or self.user.get_full_name() or self.user.username


class HourlyRate(models.Model):
    """
    An hourly rate model that serves as a way to map a provider's hourly rate per client.

    For technical details, see Django documentation, which explains intermediate models like this one:
    https://docs.djangoproject.com/en/2.0/topics/db/models/#extra-fields-on-many-to-many-relationships
    """

    # Allows up to 999999.99 of an hourly rate for some currency.
    # There are some currencies that are quite inflated. Or this provider is just really darn expensive!
    hourly_rate = MoneyField(
        max_digits=8, decimal_places=2,
        help_text=_("The hourly rate charged between a provider and client."))
    provider = models.ForeignKey(
        Account, models.CASCADE, related_name='provider_hourly_rates',
        help_text=_("The account linked to the user who gets paid the hourly rate by the client."))
    client = models.ForeignKey(
        Account, models.CASCADE, related_name='client_hourly_rates', blank=True, null=True,
        help_text=_("The account linked to the user who pays the hourly rate to the provider."))

    class Meta:
        verbose_name = _('Hourly Rate')
        verbose_name_plural = _('Hourly Rates')
        unique_together = ('provider', 'client')

    def __str__(self):
        """
        Returns a string indicating how much the provider charges the client.

        For example:
            - Expensive Consultant charges Big Enterprise 500 EUR / hour
            - Lowly Dev charges Unicorn Startup 15 EUR / hour
        """
        return '{provider} charges {client}{optional_space}{rate} / hour'.format(
            provider=str(self.provider),
            optional_space=' ' if self.client else '',
            client=str(self.client) if self.client else '',
            rate=self.hourly_rate,
        )
