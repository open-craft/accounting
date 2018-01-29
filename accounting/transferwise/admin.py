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
Admin for the TransferWise app.
"""

from django.contrib import admin

from accounting.common.admin import UuidModelAdmin
from accounting.transferwise import models


@admin.register(models.TransferWiseBulkPayment)
class TransferWiseBulkPaymentAdmin(UuidModelAdmin):
    """ Admin configuration for the `TransferWiseBulkPayment` model. """
    list_display = ('date', 'csv_path',)
    readonly_fields = ('csv_path',)


@admin.register(models.TransferWisePayment)
class TransferWisePaymentAdmin(UuidModelAdmin):
    """ Admin configuration for the `TransferWisePayment` model. """
    list_display = ('date', 'invoice',)
    search_fields = ('invoice__uuid', 'invoice__client__user__username', 'invoice__provider__user__username',)
