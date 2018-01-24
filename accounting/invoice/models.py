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
Invoice models.
"""

import logging
import os
import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
import pdfkit

from accounting.account.models import Account
from accounting.common import utils
from accounting.common.models import CommonModel, UuidModel
from accounting.invoice.choices import InvoiceApproval, InvoiceHtmlTemplate, InvoiceNumberingScheme
from accounting.third_party_api.google.mixins import GoogleDriveMixin
from accounting.third_party_api.jira.client import Jira

LOGGER = logging.getLogger(__name__)


def default_invoice_number():
    """
    Return the invoice number which defaults to `yyyy-mm` for the current year and month.
    """
    return timezone.now().strftime("%Y-%m")


class InvoiceTemplate(CommonModel, UuidModel):
    """
    A model that invoices can base off of.
    """

    provider = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name='invoice_template',
        help_text=_("The invoicing service/product provider."))
    numbering_scheme = models.CharField(
        max_length=80, choices=InvoiceNumberingScheme.choices, default=InvoiceNumberingScheme.default,
        help_text=_("The numbering scheme used to determine how to increment the invoice number."))
    extra_text = models.TextField(
        blank=True, null=True,
        help_text=_("Any arbitrary extra text that the provider would like to display on their invoice. "
                    "The HTML template that belongs to this invoice template should have a designated location "
                    "to place this extra text."))
    extra_image = models.ImageField(
        blank=True, null=True,
        help_text=_("Any arbitrary extra image that the provider would like to display on their invoice. "
                    "For example, this could be the provider's signature."))
    html_template = models.CharField(
        max_length=80, choices=InvoiceHtmlTemplate.choices, default=InvoiceHtmlTemplate.Default,
        help_text=_("The template to use to generate an invoice."))

    class Meta:
        verbose_name = _('Invoice Template')
        verbose_name_plural = _('Invoice Templates')

    def __str__(self):
        """
        Indicate between who this invoice template belongs to.
        """
        return "{provider}'s Invoice Template".format(provider=self.provider)


class Invoice(CommonModel, UuidModel, GoogleDriveMixin):
    """
    A model to hold all data related to an invoice.

    Can be used to generate actual HTML/PDF invoices off of templates.
    """

    PDF_OPTIONS = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '0mm',
        'margin-bottom': '10mm',
        'margin-left': '0mm',
        'encoding': 'UTF-8',
    }

    number = models.CharField(
        max_length=80, default=default_invoice_number,
        help_text=_("The unique invoice number. "
                    "Defaults to yyyy-mm for the current year and month."))
    date = models.DateTimeField(
        default=timezone.now,
        help_text=_("The date this invoice was created and sent for billing purposes. "
                    "Defaults to right now, but can be changed."))
    billing_start_date = models.DateTimeField(
        default=utils.get_first_day_past_month,
        help_text=_("The first date for which the line items in this invoice were provided. "
                    "Defaults to the first day of the past month."))
    billing_end_date = models.DateTimeField(
        default=utils.get_last_day_past_month,
        help_text=_("The last date for which the line items in this invoice were provided. "
                    "Defaults to the last day of the past month."))
    due_date = models.DateTimeField(
        default=utils.get_day_with_offset,
        help_text=_("When this invoice should be paid."))
    provider = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='provider_invoices',
        help_text=_("The invoicing service/product provider."))
    client = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='client_invoices',
        help_text=_("The client being invoiced for services/products."))
    paid = models.BooleanField(
        default=False,
        help_text=_("Whether this invoice has been paid by the client yet or not."))
    approved = models.CharField(
        max_length=80, choices=InvoiceApproval.choices, default=InvoiceApproval.not_approved,
        help_text=_("The approval status of this invoice."))
    pdf_path = models.URLField(
        blank=True, null=True, max_length=300,
        help_text=_("The absolute URL that can be used to retrieve the invoice PDF."))
    template = models.ForeignKey(
        InvoiceTemplate, on_delete=models.CASCADE, related_name='invoices', null=True,
        help_text=_("The template to use to generate an invoice."))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def __str__(self):
        """
        Indicate between who this invoice is, and whether it has been paid.
        """
        return '{date}: {provider} invoicing {client} ({paid})'.format(
            date=self.date,
            provider=self.provider,
            client=self.client,
            paid='PAID' if self.paid else 'PENDING',
        )

    @property
    def hourly_rate(self):
        """
        Get the `HourlyRate` object between the provider and client of this invoice.
        """
        return self.provider.provider_hourly_rates.get(client=self.client)

    @property
    def pdf_filename(self):
        """
        Return a PDF filename for this invoice.
        """
        return 'invoice_{provider}_{client}_{date}.pdf'.format(
            date=self.date.strftime("%Y-%m-%d"),
            provider=self.provider.user.username,
            client=self.client.user.username,
        )

    @property
    def total_quantity(self):
        """
        Get the total quantity of all line items on the invoice.
        """
        aggregated_quantity = self.aggregate_line_items().aggregate(total_quantity=models.Sum('quantity'))
        return aggregated_quantity['total_quantity']

    @property
    def total_cost(self):
        """
        Get the total cost of all line items on the invoice.
        """
        aggregated_cost = self.aggregate_line_items().aggregate(total_cost=models.Sum('total'))
        return aggregated_cost['total_cost']

    @property
    def is_approved(self):
        """
        Return whether this invoice has been approved or not.
        """
        return self.approved in InvoiceApproval.approved_choices()

    @property
    def html_template(self):
        """
        Get the HTML template associated with this invoice.
        """
        if self.template:
            return self.template.html_template
        return InvoiceHtmlTemplate.Default

    def aggregate_line_items(self, fields=None):
        """
        Aggregate this invoice's line items so quantities and total costs of items with the same keys are summed.

        :param fields: Which fields should be returned for each aggregated line item.
        :return: A `QuerySet` of `dict`s representing each aggregated line item. For example:
        >>> QuerySet([{
        >>>     'key': 'OC-1',
        >>>     'name': 'Hard Task',
        >>>     'price': models.DecimalField('500.00000000'),
        >>>     'quantity': models.DecimalField('1.00000000'),
        >>>     'total': models.DecimalField('500.00000000')},
        >>>     ...
        >>> ])
        """
        if fields is None:
            fields = ('key', 'name', 'price', 'quantity', 'total',)

        # This returns line items with distinct keys, names, and prices, with their quantities and totals
        # summed up into single `quantity` and `total` fields. With this, the PDF will have a single line
        # for each distinct key. For example, each line item can correspond to a single JIRA task, with
        # all worklogs summed up.
        return (self.line_items
                .values('key')
                .distinct()
                .annotate(
                    total=models.Sum(models.F('quantity') * models.F('price'), output_field=models.DecimalField()),
                    quantity=models.Sum('quantity'))
                .values(*fields)
                .order_by('-key'))

    def fill_line_items_from_jira(self):
        """
        An idempotent way to fill this Invoice's line items with JIRA worklogs.

        Each line item created through this method is tagged to be recognized as having come through JIRA. This
        allows us to only update those line items through this function that previously came from JIRA.

        Does not work if JIRA integration is disabled.

        TODO: This should be a synchronous job on a non-web worker.
        """
        if not settings.ENABLE_JIRA:
            return

        jira = Jira()
        jira_worklogs = jira.tempo_worklogs(self.provider.user.username, self.billing_start_date, self.billing_end_date)
        LOGGER.info('Received JIRA worklogs from Tempo: %s', jira_worklogs)

        jira_worklog_set = {
            (worklog.worklog_id, worklog.issue_key, worklog.issue_title, worklog.description, worklog.time_spent,)
            for worklog in jira_worklogs
        }
        line_item_set = set(self.line_items
                            .filter(tags__name__in=[LineItem.JIRA_TAG])
                            .values_list('line_item_id', 'key', 'name', 'description', 'quantity',))
        LOGGER.info('JIRA Worklog Set: %s', jira_worklog_set)
        LOGGER.info('Line Item Set: %s', line_item_set)

        # Perform any deletions.
        # Note that even if an existing worklog shares the same ID/Key as an incoming JIRA worklog, if it changed
        # in name, description, or quantity, it will be deleted. The corresponding incoming JIRA worklog is then
        # added right after. (See below).
        deleted_jira_worklogs = line_item_set - jira_worklog_set
        if deleted_jira_worklogs:
            LOGGER.info('Deleting the following JIRA worklog line items: %s', deleted_jira_worklogs)
            self.line_items.filter(
                models.Q(line_item_id__in=[worklog[0] for worklog in deleted_jira_worklogs]) &
                models.Q(key__in=[worklog[1] for worklog in deleted_jira_worklogs])
            ).delete()

        # Perform any additions and tag them as JIRA worklogs.
        # This performs a creation even for those worklogs that had previously existed but are now changed in
        # some field like name, description, or quantity. But that's okay, because they were 'refreshed' by
        # being deleted first.
        added_jira_worklogs = jira_worklog_set - line_item_set
        if added_jira_worklogs:
            LOGGER.info('Adding the following JIRA worklogs as line items: %s', added_jira_worklogs)
            for worklog in added_jira_worklogs:
                line_item = self.line_items.create(
                    invoice=self,
                    line_item_id=worklog[0],
                    key=worklog[1],
                    name=worklog[2],
                    description=worklog[3],
                    quantity=worklog[4],
                    price=self.hourly_rate.hourly_rate,
                )
                line_item.tags.add(LineItem.JIRA_TAG)

    def to_pdf(self):
        """
        Turn the invoice into a PDF using its template.

        TODO: This should be a synchronous job on a non-web worker.
        """
        template = get_template('{template}/{template}.html'.format(template=self.html_template))
        invoice = template.render({
            'site': Site.objects.get_current(),
            'invoice': self,
            'users': (
                ('provider', self.provider),
                ('client', self.client),
            ),
            'line_items': self.aggregate_line_items(),
            'currency': self.hourly_rate.hourly_rate_currency
        })
        self.pdf_path = os.path.join(settings.INVOICE_PDF_PATH, '{}.pdf'.format(uuid.uuid4()))
        pdf_configuration = pdfkit.configuration(wkhtmltopdf=settings.HTML_TO_PDF_BINARY_PATH)
        pdfkit.from_string(invoice, self.pdf_path, configuration=pdf_configuration, options=self.PDF_OPTIONS)
        return self.pdf_path


class LineItem(CommonModel):
    """
    A model to hold information related to line items to be billed through an invoice.
    """

    JIRA_TAG = 'jira_worklog'

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='line_items',
        help_text=_("The invoice to which this line item belongs."))
    line_item_id = models.IntegerField(
        help_text=_("An ID for this line item, unique with the line item key. "
                    "Can be used to store incoming ID data from 3rd parties."))
    key = models.CharField(
        max_length=100,
        help_text=_("The key identifier for this line item. "
                    "For example: OC-9999."))
    name = models.CharField(
        max_length=255,
        help_text=_("What the item is, i.e. a formal title or summary of the item."))
    description = models.TextField(
        blank=True, null=True,
        help_text=_("What this line item is about. "
                    "Optional: this will only display on invoices that have the description column."))
    quantity = models.DecimalField(
        max_digits=12, decimal_places=8,
        help_text=_("How many of these items should be billed."))
    price = MoneyField(
        max_digits=8, decimal_places=2,
        help_text=_("How much each unit of this line item costs, including the currency."))
    tags = TaggableManager(
        blank=True,
        help_text=_('A special tag for this line item. Can be used to group line items by tag.'))

    class Meta:
        verbose_name = _('Line Item')
        verbose_name_plural = _('Line Items')
        unique_together = ('invoice', 'line_item_id', 'key')

    def __str__(self):
        """
        Indicate the key and description of this line item, as well as overall costs.
        """
        return '({line_item_id}) {key} - {name} ({quantity} x {price} = {total})'.format(
            line_item_id=self.line_item_id,
            key=self.key,
            name=self.name,
            quantity=self.quantity,
            price=self.price,
            total=self.total,
        )

    @property
    def total(self):
        """
        Get the total cost and currency of this line item.
        """
        return Money(amount=(self.price.amount * self.quantity), currency=self.price.currency)
