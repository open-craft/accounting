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
Bank serializers.
"""

from rest_framework.serializers import JSONField

from accounting.address.serializers import AddressSerializer
from accounting.bank import models
from accounting.common.serializers import UuidModelSerializer


class BankSerializer(UuidModelSerializer):
    """
    Bank model serializer.
    """

    address = AddressSerializer(required=False)

    class Meta(UuidModelSerializer.Meta):
        model = models.Bank
        fields = UuidModelSerializer.Meta.fields + ('name', 'address',)


class BankAccountSerializer(UuidModelSerializer):
    """
    Bank Account serializer.
    """

    bank = BankSerializer()
    identification = JSONField()

    class Meta(UuidModelSerializer.Meta):
        model = models.BankAccount
        fields = UuidModelSerializer.Meta.fields + (
            'bank', 'type', 'identification', 'transferwise_recipient_id',
        )
