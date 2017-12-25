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
Views for the Account application.

TODO: For increased security, do the following:
TODO: 1. For views that require the user to be authenticated and change some user information,
TODO:    make sure the information being changed belongs to that user. This part should be done before deployment!
TODO:    It will require a new permission class to check if the token matches the user's.
"""

from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from accounting.account import models, serializers
from accounting.account.mixins import AccountViewMixin

USER_MODEL = get_user_model()


class AccountView(AccountViewMixin, RetrieveUpdateAPIView):
    """
    A view for retrieving and updating `Account` objects.

    Requires the username of the user linked to the account in order to find the account.
    """

    serializer_class = serializers.AccountSerializer


class CreateAccountView(AccountViewMixin, CreateAPIView):
    """
    A view for creating new `Account` objects.
    """

    serializer_class = serializers.CreateAccountSerializer


class HourlyRateView(RetrieveUpdateAPIView):
    """
    A view for retrieving and updating `HourlyRate` objects between a specific provider and client.
    """

    queryset = models.HourlyRate.objects.all()
    serializer_class = serializers.HourlyRateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Filter the `HourlyRate` object based off of the provider and client usernames from the URL.
        """
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **self.kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


class CreateHourlyRateView(CreateAPIView):
    """
    A view to create an `HourlyRate` relation between a provider and a client.
    """

    serializer_class = serializers.CreateHourlyRateSerializer
    permission_classes = (IsAuthenticated,)
