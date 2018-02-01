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
Account serializers.
"""

from django.contrib.auth import get_user_model

from accounting.account import models
from accounting.address.serializers import AddressSerializer
from accounting.authentication.serializers import UserSerializer
from accounting.bank.serializers import BankAccountSerializer
from accounting.common.serializers import UuidModelSerializer, UuidRelatedField

USER_MODEL = get_user_model()


class AccountSerializer(UuidModelSerializer):
    """
    Account model serializer.
    """

    user = UserSerializer(required=False)
    address = AddressSerializer(required=False)
    bank_account = BankAccountSerializer(required=False)

    class Meta(UuidModelSerializer.Meta):
        model = models.Account
        fields = (UuidModelSerializer.Meta.fields +
                  ('user', 'address', 'business_name', 'occupation', 'bank_account', 'vat',))


class CreateAccountSerializer(UuidModelSerializer):
    """
    Account model serializer used specifically for creating new accounts, i.e. through the registration process.

    When referencing what user or address instance this account should be linked to, we use the ID of the object.

    The hourly rate of an account is not set here -- use the returned UUID of accounts to make links between them
    through the hourly rate model.
    """

    user = UuidRelatedField(queryset=USER_MODEL.objects.filter(is_active=True))
    address = UuidRelatedField(queryset=models.Address.objects.all())

    class Meta(UuidModelSerializer.Meta):
        model = models.Account
        fields = UuidModelSerializer.Meta.fields + ('user', 'address', 'business_name', 'occupation', 'vat',)


class HourlyRateSerializer(UuidModelSerializer):
    """
    Hourly rate serializer.
    """

    provider = AccountSerializer(required=False)
    client = AccountSerializer(required=False)

    class Meta(UuidModelSerializer.Meta):
        model = models.HourlyRate
        fields = UuidModelSerializer.Meta.fields + ('hourly_rate', 'hourly_rate_currency', 'provider', 'client',)


class CreateHourlyRateSerializer(HourlyRateSerializer):
    """
    Hourly rate serializer meant specifically for creating new hourly rate links between two accounts.
    """

    provider = UuidRelatedField(queryset=models.Account.objects.all())
    client = UuidRelatedField(required=False, queryset=models.Account.objects.all())
