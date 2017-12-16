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
Account serializers.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounting.account import models
from accounting.bank.serializers import BankAccountSerializer

USER_MODEL = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    """
    Address model serializer.
    """

    id = serializers.ReadOnlyField()  # pylint: disable=invalid-name

    class Meta:
        model = models.Address
        fields = ('id', 'country', 'address_line1', 'address_line2', 'zipcode', 'city', 'state',)
        extra_kwargs = {
            'country': {'required': True},
            'address_line1': {'required': True},
            'zipcode': {'required': True},
            'city': {'required': True},
        }


class HourlyRateAccountSerializer(serializers.ModelSerializer):
    """
    Account serializer to be used by the hourly rate serializer.
    """

    address = AddressSerializer(required=False)

    class Meta:
        model = models.Account
        fields = ('user', 'address', 'business_name', 'occupation',)


class HourlyRateSerializer(serializers.ModelSerializer):
    """
    Hourly rate serializer.
    """

    hourly_rate = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    provider = HourlyRateAccountSerializer(required=False)
    client = HourlyRateAccountSerializer(required=False)

    class Meta:
        model = models.HourlyRate
        fields = ('hourly_rate', 'currency', 'provider', 'client',)

    def get_hourly_rate(self, obj):  # pylint: disable=no-self-use
        """
        Get the amount of the hourly rate.
        """
        return str(obj.hourly_rate.amount)

    def get_currency(self, obj):  # pylint: disable=no-self-use
        """
        Get the currency of the hourly rate.
        """
        return str(obj.hourly_rate.currency)


class CreateHourlyRateSerializer(serializers.ModelSerializer):
    """
    Hourly rate serializer meant specifically for creating new hourly rate links between two accounts.
    """

    id = serializers.ReadOnlyField()  # pylint: disable=invalid-name
    provider = serializers.PrimaryKeyRelatedField(queryset=models.Account.objects.all())
    client = serializers.PrimaryKeyRelatedField(required=False, queryset=models.Account.objects.all())

    class Meta:
        model = models.HourlyRate
        fields = ('id', 'hourly_rate', 'hourly_rate_currency', 'provider', 'client',)


class AccountSerializer(serializers.ModelSerializer):
    """
    Account model serializer.
    """

    address = AddressSerializer(required=False)
    bank_accounts = BankAccountSerializer(required=False, many=True)

    class Meta:
        model = models.Account
        fields = ('address', 'business_name', 'occupation', 'bank_accounts',)


class CreateAccountSerializer(serializers.ModelSerializer):
    """
    Account model serializer used specifically for creating new accounts, i.e. through the registration process.

    When referencing what user or address instance this account should be linked to, we use the ID of the object.

    The hourly rate of an account is not set here -- use the returned ID of accounts to make links between them through
    the hourly rate model.
    """

    id = serializers.ReadOnlyField()  # pylint: disable=invalid-name
    user = serializers.PrimaryKeyRelatedField(queryset=USER_MODEL.objects.filter(is_active=True))
    address = serializers.PrimaryKeyRelatedField(queryset=models.Address.objects.all())

    class Meta:
        model = models.Account
        fields = ('id', 'user', 'address', 'business_name', 'occupation',)
