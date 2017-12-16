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
Bank serializers.
"""

from rest_framework import serializers

from accounting.bank import models


# TODO: This is repeat code from accounting.account.serializers.AddressSerializer. Move it to a common app later.
class AddressSerializer(serializers.ModelSerializer):
    """
    Address model serializer.
    """

    class Meta:
        model = models.Address
        fields = ('country', 'address_line1', 'address_line2', 'zipcode', 'city', 'state',)


class BankSerializer(serializers.ModelSerializer):
    """
    Bank model serializer.
    """

    address = AddressSerializer(required=False)

    class Meta:
        model = models.Bank
        fields = ('uuid', 'name', 'address',)


class BankAccountSerializer(serializers.ModelSerializer):
    """
    Bank Account serializer.
    """

    bank = BankSerializer()

    class Meta:
        model = models.BankAccount
        fields = ('uuid', 'bank', 'currency', 'type', 'iban', 'bic', 'abn', 'bsb', 'vat',
                  'account_number', 'routing_number',)
