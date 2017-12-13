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
Account URL Configuration.
"""

from django.conf.urls import url

from accounting.account import views

USERNAME_REGEX = r'[\w.@_+-]+'
ACCOUNT_PATH_REGEX = r'(?P<user__username>{username})'.format(username=USERNAME_REGEX)
ADDRESS_PATH_REGEX = (r'address/'
                      r'(?P<accounts__user__username>{username})'.format(username=USERNAME_REGEX))
HOURLY_RATE_PATH_REGEX = (r'rate/'
                          r'(?P<provider__user__username>{username})/'
                          r'(?P<client__user__username>{username})'.format(username=USERNAME_REGEX))

account_urlpatterns = [
    url(r'^create/$',
        views.CreateAccountView.as_view()),
    url(r'^{account_path_regex}/$'.format(account_path_regex=ACCOUNT_PATH_REGEX),
        views.AccountView.as_view()),
]

hourly_rate_urlpatterns = [
    url(r'^rate/create/$',
        views.CreateHourlyRateView.as_view()),
    url(r'^{hourly_rate_path_regex}/$'.format(hourly_rate_path_regex=HOURLY_RATE_PATH_REGEX),
        views.HourlyRateView.as_view()),
]

address_urlpatterns = [
    url(r'^address/create/$',
        views.AddressView.as_view()),
    url(r'^{address_path_regex}/$'.format(address_path_regex=ADDRESS_PATH_REGEX),
        views.AddressView.as_view()),
]

urlpatterns = account_urlpatterns + hourly_rate_urlpatterns + address_urlpatterns
