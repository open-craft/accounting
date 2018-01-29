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
TransferWise mixins to be used by the Accounting service.
"""

from collections import namedtuple
import csv
import os
import uuid

from django.conf import settings

from accounting.transferwise.choices import TransferWiseCsvColumns


class TransferWiseCsvMixin:
    """
    A mixin allowing TransferWise-related classes to perform CSV operations.
    """

    CSV_ROW = namedtuple('CsvRow', list(TransferWiseCsvColumns.attributes.values()))

    def to_bulk_payment_csv(self):
        """
        Turn a list of TransferWise CSV rows into rows in a real CSV.

        Abides by the TransferWise CSV schema and generates a real CSV file in the media folder.
        """
        self.csv_path = os.path.join(settings.MEDIA_ROOT, '{}.csv'.format(uuid.uuid4()))
        with open(self.csv_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            # Write the columns first.
            writer.writerow(list(TransferWiseCsvColumns.attributes.keys()))

            # Now we can write out the recipient rows separately.
            for payment in self.payments.all():
                invoice = payment.invoice
                recipient = invoice.provider
                recipient_bank_account = recipient.active_bank_account
                client_currency = invoice.hourly_rate.hourly_rate_currency
                writer.writerow(self.CSV_ROW(
                    recipient_id=recipient_bank_account.transferwise_recipient_id,
                    name=recipient.name,
                    account=recipient_bank_account.identification['account_number'],
                    source_currency=client_currency,
                    target_currency=recipient_bank_account.identification['currency'],
                    amount_currency=client_currency,
                    amount=invoice.total_cost,
                    payment_reference=invoice.number,
                ))
        return csv_file
