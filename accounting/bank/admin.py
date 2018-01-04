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
Admin for the Bank application.
"""

from django.contrib import admin

from accounting.bank import models
from accounting.common.admin import UuidModelAdmin


@admin.register(models.Bank)
class BankAdmin(UuidModelAdmin):
    """ Admin configuration for the `Bank` model. """
    list_display = UuidModelAdmin.list_display + ('name', 'address',)


@admin.register(models.BankAccount)
class BankAccountAdmin(UuidModelAdmin):
    """ Admin configuration for the `BankAccount` model. """
    list_display = UuidModelAdmin.list_display + ('bank', 'user_account', 'type',)
