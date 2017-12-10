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
Auth views.
"""

from django.contrib.auth import login, logout

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import JSONWebTokenAPIView

from accounting.authentication.serializers import UserSerializer


class LoginView(JSONWebTokenAPIView):
    """
    View for logging in to the accounting service by providing the user a JWT.
    """

    serializer_class = JSONWebTokenSerializer
    permission_classes = (AllowAny,)

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        """
        Perform dispatch while hiding the password from logging.
        """
        return super(LoginView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Get the response from the parent JWT API View, and if the response is good, log the user in.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            login(request, self.serializer_class.validated_data['user'])  # pylint: disable=unsubscriptable-object
        return response


class LogoutView(APIView):
    """
    View for logging out from the accounting service..
    """

    def post(self, request, *args, **kwargs):
        """
        Log the user out in the Django session store.
        """
        logout(request)
        return Response({"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK)


class UserView(RetrieveUpdateAPIView):
    """
    View to define serialization of the custom User model.
    """

    serializer_class = UserSerializer
    # TODO: Update permission class to use something like `IsAuthenticatedAndIsUser`.

    def get_object(self):
        return self.request.user
