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

from datetime import timedelta
import logging
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from pydrive.drive import GoogleDrive
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
import pdfkit

from accounting.account.models import Account
from accounting.bank.choices import BankAccountIdentifiers
from accounting.common.models import UuidModel
from accounting.invoice import utils
from accounting.invoice.choices import InvoiceTemplate
from accounting.third_party_api.google.auth import GoogleAuth
from accounting.third_party_api.jira.client import Jira

LOGGER = logging.getLogger(__name__)
INVOICE_DUE_DATE_DAYS_OFFSET = 20


def get_day_with_offset(offset=INVOICE_DUE_DATE_DAYS_OFFSET):
    """
    Return the `datetime` object representing the day which comes `offset` days after today.
    """
    return timezone.now() + timedelta(days=offset)


class Invoice(UuidModel, TimeStampedModel):
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
        'encoding': "UTF-8",
    }

    number = models.CharField(
        max_length=80, default=utils.default_invoice_number,
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
        default=get_day_with_offset,
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
    extra_text = models.TextField(
        blank=True, null=True,
        help_text=_("Any arbitrary extra text that the provider would like to display on their invoice. "
                    "Each template has a designated location to place this extra text."))
    signature = models.ImageField(
        blank=True, null=True,
        help_text=_("The provider's signature."))
    template = models.CharField(
        max_length=80, choices=InvoiceTemplate.choices, default=InvoiceTemplate.Default,
        help_text=_("The template to use to generate this invoice."))
    history = HistoricalRecords()

    # TODO: The following 2 fields are temporary while we don't have a UI besides the Django admin.
    # TODO: The front-end will eventually call endpoints to do what these fields allow us to do.
    auto_download_jira_worklogs_on_save = models.BooleanField(  # pylint: disable=invalid-name
        default=False,
        help_text=_("Whether this invoice should automatically download JIRA worklogs "
                    "for the provider to fill up the invoice."))
    auto_pdf_on_save = models.BooleanField(
        default=False,
        help_text=_("Whether this invoice should be converted to a PDF on save."))
    auto_upload_google_drive_on_save = models.BooleanField(  # pylint: disable=invalid-name
        default=False,
        help_text=_("Whether this invoice should be uploaded to Google Drive when converted to a PDF on save."))

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

    def aggregate_line_items(self, fields=None):
        """
        Aggregate this invoice's line items so quantities and total costs of items with the same keys are summed.

        :param fields: Which fields should be returned for each aggregated line item.
        :return: A `QuerySet` of `dict`s representing each aggregated line item.
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
        for worklog in jira.tempo_worklogs(self.provider.user.username, self.billing_start_date, self.billing_end_date):
            line_item, created = self.line_items.filter(tags__name__in=[LineItem.JIRA_TAG]).get_or_create(
                invoice=self,
                line_item_id=worklog.worklog_id,
                key=worklog.issue_key,
                name=worklog.issue_title,
                description=worklog.description,
                quantity=worklog.time_spent,
                price=self.hourly_rate.hourly_rate,
            )
            if created:
                line_item.tags.add(LineItem.JIRA_TAG)

    def to_pdf(self):
        """
        Turn the invoice into a PDF using its template.

        If successful, returns the filename of the generated PDF.

        TODO: This should be a synchronous job on a non-web worker.
        """
        # Get an aggregated set of data to reduce the length of the invoice.
        aggregated_line_items = self.aggregate_line_items()
        aggregated_quantity = aggregated_line_items.aggregate(total_quantity=models.Sum('quantity'))
        aggregated_cost = aggregated_line_items.aggregate(total_cost=models.Sum('total'))

        # Get only the bank account details that exist for the provider.
        provider_bank_account = self.provider.bank_accounts.first()
        provider_bank_account_details = tuple(
            (name, provider_bank_account.identification[key])
            for key, name in BankAccountIdentifiers.choices
            if provider_bank_account.identification[key]
        )

        template = get_template('{template}/{template}.html'.format(template=self.template))
        invoice = template.render({
            'site': Site.objects.get_current(),
            'invoice': self,
            'users': (
                ('provider', self.provider),
                ('client', self.client),
            ),
            'bank_account': provider_bank_account,
            'bank_account_details': provider_bank_account_details,
            'line_items': aggregated_line_items,
            'total_quantity': aggregated_quantity['total_quantity'],
            'total_cost': aggregated_cost['total_cost'],
            'currency': self.hourly_rate.hourly_rate_currency
        })
        pdf_name = 'invoice_{provider}_{client}_{date}.pdf'.format(
            date=self.date.strftime("%Y-%m-%d"),
            provider=self.provider.user.username,
            client=self.client.user.username,
        )
        pdf_path = os.path.join(settings.INVOICE_PDF_PATH, pdf_name)
        pdf_configuration = pdfkit.configuration(wkhtmltopdf=settings.HTML_TO_PDF_BINARY_PATH)
        pdfkit.from_string(invoice, pdf_path, configuration=pdf_configuration, options=self.PDF_OPTIONS)
        return pdf_path

    def upload_to_google_drive(self, invoice_file):  # NOQA
        """
        Upload the invoice in some file format to Google Drive.

        Assumes the invoice has already been turned into a file, i.e. a PDF.
        Assumes a _very_ specific file structure right now. For example:
            |- 2016
            |- 2017
            |   |- blah
            |   |- invoices-in
            |   |   |- 1
            |   |   |- 2
            |   |   |- ...
            |   |   |- 12
            |   |       |- invoice.pdf
            |   |- invoices-out
            |- 2018

        TODO: This should be a synchronous job on a non-web worker.
        """
        if not settings.ENABLE_GOOGLE:
            return

        # Generate a query we'll use repeatedly for finding the proper folder.
        query = ("mimeType ='application/vnd.google-apps.folder' and "
                 "'{}' in parents and "
                 "trashed=false")

        def get_folder_id(root, name):
            """ Returns the ID of the folder with name `name` in the folder given by ID `root`. """
            folders = drive.ListFile({'q': query.format(root)}).GetList()
            for folder in folders:
                if folder['title'] == name:
                    return folder['id']

        gauth = GoogleAuth()
        gauth.ServiceAuth()
        drive = GoogleDrive(gauth)
        year_folder = get_folder_id(settings.GOOGLE_DRIVE_ROOT, str(self.billing_start_date.year))
        invoice_folder = get_folder_id(year_folder, 'invoices-in')
        month_folder = get_folder_id(invoice_folder, str(self.billing_start_date.month))
        file = drive.CreateFile({
            'title': invoice_file.split('/')[-1],
            'parents': [{'id': month_folder}]
        })
        file.SetContentFile(invoice_file)
        file.Upload()

    def save(self, **kwargs):
        """
        Convert the invoice to a PDF and/or upload it to Google Drive after a successful save.
        """
        super().save(**kwargs)
        if self.auto_download_jira_worklogs_on_save:
            self.fill_line_items_from_jira()
        if self.auto_pdf_on_save:
            pdf = self.to_pdf()
            if self.auto_upload_google_drive_on_save:
                self.upload_to_google_drive(pdf)


class LineItem(models.Model):
    """
    A model to hold information related to line items to be billed through an invoice.
    """

    JIRA_TAG = 'jira_worklog'

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='line_items',
        help_text=_("The invoice to which this line item belongs."))
    line_item_id = models.IntegerField(
        help_text=_("A non-auto-incrementing ID used for line items with the same fields for when the "
                    "items may be the same or different. "
                    "For example: a line item may have the exact same descriptive fields but still be "
                    "a separate physical item, in which case a UUID or auto-incrementing ID would not suffice "
                    "to tell the difference."))
    key = models.CharField(
        max_length=100,
        help_text=_("The key identifier for this line item. "
                    "For example: OC-9999."))
    name = models.CharField(
        max_length=255,
        help_text=_("What the item is."))
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
        unique_together = ('line_item_id', 'key')

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
