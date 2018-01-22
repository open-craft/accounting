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
Invoice utilities.
"""

import datetime

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template.loader import get_template

from accounting.account.models import Account
from accounting.common.utils import get_last_day_past_month
from accounting.invoice import choices, models


def resolve_dict_callables(dictionary, *args):
    """
    Resolve any potential callables in a dictionary by passing it some arguments.

    We use a new dictionary to prevent mutating the callable. If we didn't, then on another round of calling this
    with the same dictionary, the callable would have disappeared.

    Example without using a new dictionary:
    >>> d = {
    >>>     'a': lambda a: a**2
    >>>     'b': 'str'
    >>> }
    >>> resolve_dict_callables(d, 4)
    >>> print(d)
    >>> # We lose the callable.
    >>> {'a': 16, 'b': 'str'}
    """
    new_dict = {}
    for key, potential_callable in dictionary.items():
        if callable(potential_callable):
            new_dict[key] = potential_callable(*args)
        else:
            new_dict[key] = dictionary[key]
    return new_dict


def upload_invoice_to_google_drive(invoice, draft_invoice=False):
    """
    Upload an invoice to Google Drive.

    :param invoice: The invoice to upload.
    :param draft_invoice: Whether this invoice should be uploaded into a 'draft' directory.
    :return:
    """
    target_path = [invoice.date.strftime('%Y'), 'invoices-in', invoice.date.strftime('%m')]
    if draft_invoice:
        # Insert a draft folder before the last invoice-containing folder.
        target_path.insert(-1, 'draft')
    file = invoice.upload_to_google_drive(
        file_path=invoice.pdf_path,
        target_path=target_path,
        title=invoice.pdf_filename,
    )
    invoice.pdf_path = file['webContentLink']
    invoice.save()


# pylint: disable=too-many-arguments,too-many-locals
def send_email_with_invoice(template, subject, extra_email_context=None, client_usernames=settings.BILLING_CYCLE_USERS,
                            create_invoice=False, draft_invoice=False, fill_line_items_from_jira=False,
                            upload_to_google_drive=False, auto_approve=False):
    """
    Send an email with an invoice attached, and potentially perform peripheral actions.

    TODO: This function's pretty beefy; break it up by encapsulating logic into more utility functions or a new class.

    :param template: The email template.
    :param subject: The email subject.
    :param extra_email_context: Extra kwargs to update the email context with.
    :param client_usernames: The list of billing cycle users' usernames.
    :param create_invoice: Whether to create a new invoice based off of a past one.
    :param draft_invoice: Whether this is a draft invoice or not.
    :param fill_line_items_from_jira: Whether to fill up the invoice's line items from JIRA worklogs.
    :param upload_to_google_drive: Whether to upload the resulting invoice PDF to Google Drive.
                                   If using a draft invoice, it gets uploaded into `invoices-in/draft/{month}`.
    """
    if extra_email_context is None:
        extra_email_context = {}
    now = datetime.datetime.now()
    past = get_last_day_past_month()
    past_month_formatted = past.strftime('%B')
    template = get_template(template)
    for client_username in client_usernames:
        client = Account.objects.get(user__username=client_username)
        providers = [rate.provider for rate in client.client_hourly_rates.filter(active=True)]
        for provider in providers:
            try:
                invoice = models.Invoice.objects.filter(
                    provider=provider,
                    client=client,
                    date__month=past.month if draft_invoice else now.month,
                ).latest('date')
            except models.Invoice.DoesNotExist:
                # This may be the provider's first invoice.
                invoice = None

            if create_invoice or not invoice:
                invoice = models.Invoice.objects.create(
                    number=choices.InvoiceNumberingScheme.increment_value(
                        invoice.template.numbering_scheme,
                        invoice.number
                    ) if invoice else choices.InvoiceNumberingScheme.default_value(
                        provider.invoice_template.numbering_scheme
                    ),
                    provider=provider,
                    client=client,
                    template=provider.invoice_template,
                )
            if fill_line_items_from_jira:
                invoice.fill_line_items_from_jira()

            # Make the email, attach the invoice, and send it.
            message_context = {'month': past_month_formatted, 'contact_email': client.user.email}
            message_context.update(**resolve_dict_callables(extra_email_context, invoice))
            message = template.render(message_context)
            email = EmailMessage(
                subject=subject.format(month=past_month_formatted),
                body=message,
                to=[provider.user.email],
                cc=[client.user.email],
            )
            email.attach_file(invoice.to_pdf())
            email.send()

            # Upload the invoice to a directory in GDrive.
            if upload_to_google_drive:
                upload_invoice_to_google_drive(invoice, draft_invoice=draft_invoice)
            if auto_approve and not invoice.is_approved:
                invoice.approved = choices.InvoiceApproval.automatically
            invoice.save()
