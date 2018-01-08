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

# pylint: disable=unused-variable,no-self-use
"""
Management command for generating data (usually for a development environment) to play with.
"""

import logging

from django.core.management import BaseCommand
from django.db import IntegrityError, transaction

from accounting.account.tests import factories
from accounting.bank.tests.factories import BankAccountFactory

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A management command to generate data for the Account application.

    Specifically, generate `HourlyRate` objects between generated `Account` objects.
    Also optionally create `BankAccount` objects.
    """

    help = 'Generate data for the Account app, usually to play with in a development environment.'

    DEFAULT_ACCOUNTS_NUM = 10
    DEFAULT_PASSWORD = 'password'  # NOQA
    DEFAULT_IS_STAFF = False
    DEFAULT_IS_SUPERUSER = False
    DEFAULT_CREATE_BANK_ACCOUNTS = True

    def add_arguments(self, parser):
        """
        Entry point for custom arguments.
        """
        parser.add_argument(
            '--accounts-num',
            action='store',
            dest='accounts_num',
            type=int,
            default=self.DEFAULT_ACCOUNTS_NUM,
            help='The number of accounts to generate, including address and hourly rate data. Use an even number, '
                 'since we use the HourlyRate factory to generate accounts, which needs 2 accounts '
                 '(provider and client) per instance. '
                 'By default, generates 10 accounts.'
        )
        parser.add_argument(
            '--password',
            action='store',
            dest='password',
            default=self.DEFAULT_PASSWORD,
            help='The password to set for all created accounts. '
                 'By default, sets `password` as the password.'
        )
        parser.add_argument(
            '--is-staff',
            action='store',
            dest='is_staff',
            type=bool,
            default=self.DEFAULT_IS_STAFF,
            help='The staff status to set for all created accounts. '
                 'By default, does not make any generated accounts staff.'
        )
        parser.add_argument(
            '--is-superuser',
            action='store',
            dest='is_superuser',
            type=bool,
            default=self.DEFAULT_IS_SUPERUSER,
            help='The superuser status to set for all created accounts. '
                 'By default, does not make generated accounts superuser.'
        )
        parser.add_argument(
            '--bank-accounts',
            action='store',
            dest='bank_accounts',
            type=bool,
            default=self.DEFAULT_CREATE_BANK_ACCOUNTS,
            help='Whether or not to generate bank accounts as well as user accounts. '
                 'By default, does generate bank accounts in addition to user accounts.'
        )

    def handle(self, *args, **options):
        """
        The actual logic of the command.
        """
        accounts_num = options.get('accounts_num') // 2
        password = options.get('password')
        is_staff = options.get('is_staff')
        is_superuser = options.get('is_superuser')
        bank_accounts = options.get('bank_accounts')
        for __ in range(accounts_num):
            hourly_rate = self.make_hourly_rate()
            self.update_account(hourly_rate.provider, is_staff=is_staff, is_superuser=is_superuser, password=password)
            self.update_account(hourly_rate.client, is_staff=is_staff, is_superuser=is_superuser, password=password)
            LOGGER.info('Created %s', hourly_rate.provider)
            LOGGER.info('Created %s', hourly_rate.client)
            if bank_accounts:
                BankAccountFactory(user_account=hourly_rate.provider)
                BankAccountFactory(user_account=hourly_rate.client)

    def make_hourly_rate(self):
        """
        Make an hourly rate object which in turn creates account objects.
        """
        try:
            with transaction.atomic():
                return factories.HourlyRateFactory()
        except IntegrityError:
            # If there was a conflict in our auto-generation (can happen easily for large values of `accounts_num`),
            # call the function again to ensure we make the target number of accounts.
            return self.make_hourly_rate()

    def update_account(self, account, is_staff=DEFAULT_IS_STAFF, is_superuser=DEFAULT_IS_SUPERUSER,
                       password=DEFAULT_PASSWORD):  # NOQA
        """
        Set sensitive details for each generated account.
        """
        account.is_staff = is_staff
        account.is_superuser = is_superuser
        account.user.set_password(password)
        account.save()
