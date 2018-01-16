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
Invoice tasks.
"""

from urllib.parse import urljoin
import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMessage
from django.template.loader import get_template
from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from rest_framework.reverse import reverse

from accounting.account.models import Account
from accounting.common.utils import get_last_day_past_month
from accounting.invoice import constants
from accounting.invoice.utils import send_email_with_invoice


@db_periodic_task(crontab(day=settings.INVOICE_NOTIFICATION_DAY, hour="0", minute="0"))
def send_invoice_prep_notification():
    """
    Send emails to notify invoice recipients to prepare for invoice receipt.
    """
    now = datetime.datetime.now()
    approval_date = now.replace(day=int(settings.INVOICE_APPROVAL_DAY))
    past_month = get_last_day_past_month().strftime('%B')
    template = get_template(constants.INVOICE_NOTIFICATION_TEMPLATE)
    for client_username in settings.BILLING_CYCLE_USERS:
        client = Account.objects.get(user__username=client_username)
        provider_emails = [rate.provider.user.email for rate in client.client_hourly_rates.all()]
        message = template.render({'approval_date': approval_date, 'month': past_month})
        EmailMessage(
            subject=constants.INVOICE_NOTIFICATION_SUBJECT.format(month=past_month),
            body=message,
            bcc=provider_emails,
            cc=[client.user.email],
        ).send()


@db_periodic_task(crontab(day=settings.INVOICE_APPROVAL_DAY, hour="0", minute="0"))
def send_invoice_approval_request():
    """
    Send emails containing invoices and links to approve those invoices.
    """
    base_site_url = Site.objects.get_current().domain
    send_email_with_invoice(
        constants.INVOICE_APPROVAL_TEMPLATE,
        constants.INVOICE_APPROVAL_SUBJECT,
        extra_email_context={
            'approval_url': lambda invoice: urljoin(
                base_site_url,
                reverse('invoice:invoice-approve', [invoice.uuid])
            ),
            'final_date': datetime.datetime.now().replace(day=int(settings.INVOICE_FINAL_DAY))
        },
        create_invoice=True,
        draft_invoice=True,
        fill_line_items_from_jira=True,
        upload_to_google_drive=True,
    )


@db_periodic_task(crontab(day=settings.INVOICE_FINAL_DAY, hour="0", minute="0"))
def send_final_invoices():
    """
    Send emails containing finalized invoices.
    """
    send_email_with_invoice(
        constants.INVOICE_FINAL_TEMPLATE,
        constants.INVOICE_FINAL_SUBJECT,
        upload_to_google_drive=True,
        auto_approve=True,
    )
