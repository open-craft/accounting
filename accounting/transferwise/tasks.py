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
TransferWise tasks.
"""

from django.conf import settings
from django.core.mail.message import EmailMessage
from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from accounting.transferwise import models


@db_periodic_task(crontab(day=settings.TRANSFERWISE_BULK_PAYMENT_DAY, hour="0", minute="0"))
def send_bulk_payment_csv():
    """ Generate a bulk payment CSV, send it to the designated TransferWise Bulk Payment sender via e-mail,
    and upload it to Google Drive. """
    # Make the new bulk payment for the sender.
    bulk_payment = models.TransferWiseBulkPayment.objects.create()
    bulk_payment.create_payments()
    bulk_payment_csv = bulk_payment.to_bulk_payment_csv()

    # Make the email, attach the CSV and send.
    email = EmailMessage(
        subject='TransferWise Bulk Payment CSV',
        body='TransferWise Bulk Payment CSV is attached.',
        to=[bulk_payment.sender.user.email],
    )
    email.attach_file(bulk_payment_csv.name)
    email.send()

    # Upload to GDrive.
    file = bulk_payment.upload_to_google_drive(
        file_path=bulk_payment.csv_path,
        target_path=[bulk_payment.date.strftime('%Y'), 'invoices-in', bulk_payment.date.strftime('%m')],
        title=bulk_payment.csv_filename,
    )
    bulk_payment.csv_path = file['alternateLink']
    bulk_payment.save()
