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
from django.utils.html import format_html
from rangefilter.filter import DateRangeFilter

from accounting.common.admin import UuidModelAdmin
from accounting.transferwise import models


# pylint: disable=no-self-use
@admin.register(models.TransferWiseBulkPayment)
class TransferWiseBulkPaymentAdmin(UuidModelAdmin):
    """ Admin configuration for the `TransferWiseBulkPayment` model. """

    list_display = ('__str__', 'csv_link',)
    list_filter = (('date', DateRangeFilter),)
    readonly_fields = ('csv_link',)
    exclude = ('csv_path',)

    def csv_link(self, instance):
        """The bulk payment's clickable CSV path."""
        return format_html(
            '<a href="{url}">Click here to see CSV.</a>',
            url=instance.csv_path
        ) if instance.csv_path else 'No CSV available.'


@admin.register(models.TransferWisePayment)
class TransferWisePaymentAdmin(UuidModelAdmin):
    """ Admin configuration for the `TransferWisePayment` model. """

    list_display = ('__str__', 'invoice',)
    list_filter = (('date', DateRangeFilter),)
    search_fields = ('invoice__uuid', 'invoice__client__user__username', 'invoice__provider__user__username',)
