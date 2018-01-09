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
TransferWise choices to be used by the Accounting service.
"""

from django.utils.translation import ugettext_lazy as _
from djchoices import ChoiceItem, DjangoChoices


class TransferWiseCsvColumns(DjangoChoices):
    """
    Represents the columns in TransferWise bulk payment CSVs.
    """
    recipient_id = ChoiceItem('recipientId', _('Recipient Identifier'))
    name = ChoiceItem('name', _('Recipient Name'))
    account = ChoiceItem('account', _('Recipient Account Identifier'))
    source_currency = ChoiceItem('sourceCurrency', _('Source Currency'))
    target_currency = ChoiceItem('targetCurrency', _('Target Currency'))
    amount_currency = ChoiceItem('amountCurrency', _('Amount Currency'))
    amount = ChoiceItem('amount', _('Transfer Amount'))
    payment_reference = ChoiceItem('paymentReference', _('Payment Reference'))
