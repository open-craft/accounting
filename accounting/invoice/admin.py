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

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from rangefilter.filter import DateRangeFilter
from simple_history.admin import SimpleHistoryAdmin

from accounting.common.admin import UuidModelAdmin
from accounting.invoice import choices, models


@admin.register(models.InvoiceTemplate)
class InvoiceTemplateAdmin(UuidModelAdmin):
    """ Admin configuration for the `InvoiceTemplate` model. """

    list_display = UuidModelAdmin.list_display + ('provider', 'numbering_scheme',)
    search_fields = ('provider__user__username',)


# pylint: disable=no-self-use
@admin.register(models.Invoice)
class InvoiceAdmin(UuidModelAdmin, SimpleHistoryAdmin):
    """ Admin configuration for the `Invoice` model. """

    list_display = ('__str__', 'provider', 'client', 'total', 'pdf_link', 'jira_timesheet_link', 'approved', 'paid',)
    list_filter = (('date', DateRangeFilter),)
    search_fields = ('provider__user__username', 'client__user__username',)
    readonly_fields = ('pdf_link', 'jira_timesheet_link', 'total',)
    actions = ['mark_paid', 'mark_approved']
    exclude = ('pdf_path',)

    def total(self, instance):
        """The total charge of this invoice, given in the currency of the hourly rate between provider and client."""
        total_cost = instance.total_cost
        currency = instance.hourly_rate.hourly_rate_currency
        return '{cost:0.2f} {currency}'.format(cost=total_cost, currency=currency)

    def pdf_link(self, instance):
        """The invoice's clickable PDF path."""
        return format_html(
            '<a href="{url}">Click here to see PDF.</a>',
            url=instance.pdf_path
        ) if instance.pdf_path else 'No PDF available.'

    def jira_timesheet_link(self, instance):
        """The JIRA timesheet associated with this invoice's JIRA line items."""
        return format_html('<a href="{url}">Click here to see JIRA worklogs.</a>', url=(
            '{base}/secure/TempoUserBoard!timesheet.jspa'
            '?userId={provider_username}'
            '&periodType=BILLING'
            '&periodView=DATES'
            '&from={from_date}'
            '&to={to_date}'
        ).format(
            base=settings.JIRA_SERVER_URL,
            provider_username=instance.provider.user.username,
            from_date=instance.billing_start_date.strftime('%Y-%m-%d'),
            to_date=instance.billing_end_date.strftime('%Y-%m-%d'),
        ))

    def mark_paid(self, request, queryset):
        """Mark selected invoices as paid."""
        queryset.update(paid=True)
    mark_paid.short_description = mark_paid.__doc__

    def mark_approved(self, request, queryset):
        """Mark selected invoices as approved."""
        queryset.filter(
            approved__in=choices.InvoiceApproval.not_approved_choices()
        ).update(
            approved=choices.InvoiceApproval.manually
        )
    mark_approved.short_description = mark_approved.__doc__


@admin.register(models.LineItem)
class LineItemAdmin(admin.ModelAdmin):
    """ Admin configuration for the `LineItem` model. """

    list_display = ('key', 'description', 'quantity', 'price',)
    search_fields = ('key', 'invoice__uuid',)
