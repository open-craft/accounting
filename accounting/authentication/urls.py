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
Auth URL Configuration.
"""

from django.conf.urls import url

from accounting.account.urls import USERNAME_REGEX
from accounting.authentication.views import ObtainAuthToken, RevokeAuthToken, UserView, VerifyAuthToken

token_urlpatterns = [
    url(r'^token/obtain/', ObtainAuthToken.as_view()),
    url(r'^token/revoke/', RevokeAuthToken.as_view()),
    url(r'^token/verify/', VerifyAuthToken.as_view()),
]

urlpatterns = [
    url(r'^user/(?P<username>{username})/$'.format(username=USERNAME_REGEX), UserView.as_view()),
] + token_urlpatterns
