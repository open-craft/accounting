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
Administration for Account models.
"""

from django.contrib import admin

from accounting.account import models
from accounting.common.admin import UuidModelAdmin


@admin.register(models.Account)
class AccountAdmin(UuidModelAdmin):
    """ Admin configuration for the `Account` model. """
    list_display = ('user', 'address', 'business_name', 'occupation', 'vat',)


@admin.register(models.HourlyRate)
class HourlyRateAdmin(UuidModelAdmin):
    """ Admin configuration for the `HourlyRate` model. """
    list_display = ('hourly_rate', 'provider', 'client',)
