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
TransferWise models to be used by the Accounting service.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from accounting.account.models import Account
from accounting.common.models import CommonModel, UuidModel
from accounting.invoice.models import Invoice
from accounting.third_party_api.google.mixins import GoogleDriveMixin
from accounting.transferwise.mixins import TransferWiseCsvMixin


def ancient_date():
    """ Return the date accounting was born. """
    return timezone.now().replace(year=1)


class TransferWiseBulkPayment(CommonModel, UuidModel, TransferWiseCsvMixin, GoogleDriveMixin):
    """
    A model that represents TransferWise bulk payments.

    Can be used to generate bulk payment CSVs.
    """

    date = models.DateTimeField(
        default=timezone.now,
        help_text=_("The date this bulk payment was created and uploaded to TransferWise. "
                    "Defaults to right now, but can be changed."))
    start_date = models.DateTimeField(
        default=ancient_date,
        help_text=_("The start of the date interval for which to consider unpaid invoices for. "
                    "Defaults to an ancient date."))
    end_date = models.DateTimeField(
        default=timezone.now,
        help_text=_("The end of the date interval for which to consider unpaid invoices for. "
                    "Defaults to the last day of the past month."))
    csv_path = models.URLField(
        blank=True, null=True, max_length=300,
        help_text=_("The absolute URL that can be used to retrieve the bulk payment CSV."))

    class Meta:
        verbose_name = _('TransferWise Bulk Payment')
        verbose_name_plural = _('TransferWise Bulk Payments')

    def __str__(self):
        """
        Indicate who's sending this TransferWise bulk payment, and when.
        """
        return '{date}: {sender}'.format(date=self.date, sender=self.sender)

    @property
    def csv_filename(self):
        """
        Return a CSV filename for this bulk payment.
        """
        return 'transferwise_bulk_payment_csv_{sender}_{date}.csv'.format(
            sender=self.sender.user.username,
            date=self.date.strftime("%Y-%m-%d"),
        )

    @property
    def sender(self):
        """
        Return the sender account.
        """
        return Account.objects.get(user__username=settings.TRANSFERWISE_BULK_PAYMENT_SENDER)

    def create_payments(self):
        """
        Create the individual TransferWise payments needed for this bulk payment.

        The chosen invoices are those that are:

        * Unpaid
        * Within this bulk payment's date range (start_date, end_date).
        * Owned by a provider who's eligible for TransferWise transfers.

        Note that the invoice is the source of truth for payments, and thus should exist before making a payment.

        TODO: Besides creating an internal version of the payment for tracking certain data (i.e. recipient ID,
        TODO: invoice, etc.), this should eventually actually call the API to create real transfers. At that stage,
        TODO: we could then skip generating CSVs and create all the transfers in one go, and call them a 'bulk payment',
        TODO: even if that terminology is only to represent how we're doing it internally.
        """
        unpaid_invoices = self.sender.client_invoices.filter(
            paid=False,
            date__range=(self.start_date, self.end_date),
            provider__bank_accounts__transferwise_recipient_id__isnull=False,
        )
        for unpaid_invoice in unpaid_invoices:
            self.payments.create(bulk_payment=self, invoice=unpaid_invoice)
            unpaid_invoice.paid = True
            unpaid_invoice.save()


class TransferWisePayment(CommonModel, UuidModel):
    """
    A model to track parts of a TransferWise payment that TransferWise does not, e.g. invoices and bulk payments.
    """

    date = models.DateTimeField(
        default=timezone.now,
        help_text=_("The date this payment was made. "
                    "Defaults to right now, but can be changed."))
    bulk_payment = models.ForeignKey(
        TransferWiseBulkPayment, on_delete=models.CASCADE, related_name='payments', blank=True, null=True,
        help_text=_("The TransferWise bulk payment that this payment may be a part of."))
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, related_name='transferwise_payment', unique=True,
        help_text=_("The invoice to which this TransferWise payment belongs."))

    class Meta:
        verbose_name = _('TransferWise Payment')
        verbose_name_plural = _('TransferWise Payments')

    def __str__(self):
        """
        Indicate between whom this payment was made, and when.
        """
        return '{date}: {client} paid {provider}'.format(
            date=self.date,
            client=self.invoice.client,
            provider=self.invoice.provider,
        )
