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

from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken as UpstreamObtainAuthToken
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.authentication.serializers import AuthTokenVerificationSerializer, UserSerializer

USER_MODEL = get_user_model()


class ObtainAuthToken(UpstreamObtainAuthToken):
    """
    A simple override of the upstream `ObtainAuthToken` view to change certain class-level defaults.
    """

    serializer_class = AuthTokenSerializer


class RevokeAuthToken(APIView):
    """
    View to allow revoking authentication tokens for users.
    """

    serializer_class = AuthTokenVerificationSerializer

    def post(self, request, *args, **kwargs):
        """
        Revoke an authentication token for a user.

        Expects a `username` to identify the user, and the `token` to confirm that the request
        is coming from the token holder.

        If the user fails to retrieve, or is inactive, or the token doesn't belong to this user,
        an error message is returned indicating what the particular issue was.
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            Token.objects.get(key=user.auth_token.key, user=user).delete()
            return Response()
        except serializers.ValidationError as err:
            return Response({'error': err.detail}, status=status.HTTP_304_NOT_MODIFIED)


class VerifyAuthToken(APIView):
    """
    View that allows verifying the existence of an authentication token for a user.
    """

    serializer_class = AuthTokenVerificationSerializer

    def post(self, request, *args, **kwargs):
        """
        Verify an authentication token exists for a user.

        Expects a `username` to identify the user, and the `token` to confirm that the request
        is coming from the token holder.

        Returns a dictionary with the following key/value pairs:
            exists: Whether the token exists for this user.
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        return Response({'exists': serializer.is_valid()})


class UserView(RetrieveUpdateAPIView):
    """
    View to define serialization of the custom User model.
    """

    lookup_field = 'username'
    queryset = USER_MODEL.objects.filter(is_active=True)
    serializer_class = UserSerializer
