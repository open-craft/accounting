# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2017 OpenCraft <xavier@opencraft.com>
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
Views for registration.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from simple_email_confirmation.exceptions import EmailConfirmationExpired
from simple_email_confirmation.models import EmailAddress

from accounting.authentication.serializers import CreateUserSerializer
from accounting.registration.utils import send_email_verification

USER_MODEL = get_user_model()


class RegistrationView(CreateAPIView):
    """
    View to register a user and send a verification email.
    """

    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        """
        Override the create hook to send a verification email.
        """
        super().perform_create(serializer)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user = USER_MODEL.objects.get(email=email, username=username)
        email = EmailAddress.objects.create_unconfirmed(email, user)
        send_email_verification(email, self.request)


class VerifyRegistrationEmailView(APIView):
    """
    View that receives requests for email verification.
    """

    def get(self, request, code, *args, **kwargs):
        """
        Attempt to confirm an email verification code.

        Email verification codes may either not exist, or be expired.

        Returns the following keys:
            email: The email attached to the code that should be confirmed.
            verified: Whether verification was successful.
            expired: Whether the verification email expired.
        """
        email = None
        verified = expired = False
        response_status = status.HTTP_200_OK
        try:
            email = EmailAddress.objects.confirm(code).email
        except EmailAddress.DoesNotExist:
            response_status = status.HTTP_404_NOT_FOUND
        except EmailConfirmationExpired:
            expired = True
        else:
            expired = False
            verified = True
        return Response({
            'email': email,
            'verified': verified,
            'expired': expired,
        }, status=response_status)
