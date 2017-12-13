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
Auth serializers.
"""

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from accounting.account.serializers import AccountSerializer

USER_MODEL = get_user_model()


class AuthTokenVerificationSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializer used to verify the existence of an authentication token linked to a user.
    """

    username = serializers.CharField(label=_("Username"))
    token = serializers.CharField(label=_("Token"), trim_whitespace=False)

    def validate(self, attrs):
        """
        Check that a `username` and `token` value can be used to get an active user with the input token value.
        """
        username = attrs.get('username')
        token = attrs.get('token')

        if username and token:
            try:
                user = USER_MODEL.objects.get(username=username, auth_token__key=token)
                if not user.is_active:
                    msg = _("User {} is not active.").format(username)
                    raise serializers.ValidationError(msg, code='authorization')
            except USER_MODEL.DoesNotExist:
                msg = _('No such user with username {} and token {}.').format(username, token)
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "token".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    User model serializer.
    """

    account = AccountSerializer(required=False)

    class Meta:
        model = USER_MODEL
        fields = ('username', 'email', 'first_name', 'last_name', 'account',)


class CreateUserSerializer(serializers.ModelSerializer):
    """
    User model serializer used specifically for creating new users, i.e. through registration.
    """

    id = serializers.ReadOnlyField()  # pylint: disable=invalid-name

    class Meta:
        model = USER_MODEL
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name',)
        extra_kwargs = {
            'username': {'required': True},
            'password': {'required': True, 'write_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        """
        Along with actually creating the User model, set the password.
        """
        super().create(validated_data)
        user = USER_MODEL.objects.get(email=validated_data['email'], username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user
