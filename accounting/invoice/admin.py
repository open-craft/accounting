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
Administration for Invoices.
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from accounting.common.admin import UuidModelAdmin
from accounting.invoice import models


@admin.register(models.Invoice)
class InvoiceAdmin(UuidModelAdmin, SimpleHistoryAdmin):
    """ Admin configuration for the `Invoice` model. """
    list_display = ('number', 'provider', 'client', 'due_date', 'paid',)
    search_fields = ('provider__user__username', 'client__user__username',)
    readonly_fields = ('pdf_path',)


@admin.register(models.LineItem)
class LineItemAdmin(admin.ModelAdmin):
    """ Admin configuration for the `LineItem` model. """
    list_display = ('key', 'description', 'quantity', 'price',)
    search_fields = ('key', 'invoice__uuid',)
