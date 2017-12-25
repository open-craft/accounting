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
Bank choices.
"""

from django.utils.translation import ugettext_lazy as _
from djchoices import ChoiceItem, DjangoChoices


class BankAccountIdentifiers(DjangoChoices):
    """
    Choices for bank account identification.

    This matches what TransferWise works with for bank identification.
    It should be kept up to date depending on the API version used.
    """
    BIC = ChoiceItem('bic', _('BIC'))
    IBAN = ChoiceItem('iban', _('IBAN'))
    ABARTN = ChoiceItem('abartn', _('Routing Number'))
    ACCOUNT_NUMBER = ChoiceItem('accountNumber', _('Account Number'))
    BANK_CODE = ChoiceItem('bankCode', _('Bank Code'))
    BANK_GIRO_NUMBER = ChoiceItem('bankgiroNumber', _('Bank Giro Number'))
    BRANCH_CODE = ChoiceItem('branchCode', _('Bank Branch Code'))
    BSB_CODE = ChoiceItem('bsbCode', _('BSB Code'))
    CARD_NUMBER = ChoiceItem('cardNumber', _('Union Pay Card Number'))
    CLABE = ChoiceItem('clabe', _('CLABE'))
    IFSC_CODE = ChoiceItem('ifscCode', _('IFSC Code'))
    INSTITUTION_NUMBER = ChoiceItem('institutionNumber', _('Canadian Institution Number'))
    ROUTING_NUMBER = ChoiceItem('routingNumber', _('Routing Number'))
    SORT_CODE = ChoiceItem('sortCode', _('Bank Sort Code'))
    SWIFT_CODE = ChoiceItem('swiftCode', _('Bank SWIFT Code'))
    TRANSIT_NUMBER = ChoiceItem('transitNumber', _('Transit Number'))


class BankAccountType(DjangoChoices):
    """
    Choices for bank account types.
    """
    CHECKING = ChoiceItem('checking', _('Checking Account'))
    SAVINGS = ChoiceItem('savings', _('Savings Account'))
