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
Views for the Bank application.
"""

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from accounting.bank import models, serializers


class BankView(RetrieveUpdateAPIView):
    """
    A view for retrieving and updating `Bank` objects.
    """

    lookup_field = 'uuid'
    queryset = models.Bank.objects.all()
    serializer_class = serializers.BankSerializer
    permission_classes = (IsAuthenticated,)


class BankAccountView(RetrieveUpdateAPIView):
    """
    A view for retrieving and updating `BankAccount` objects.
    """

    lookup_field = 'uuid'
    queryset = models.BankAccount.objects.all()
    serializer_class = serializers.BankAccountSerializer
    permission_classes = (IsAuthenticated,)
