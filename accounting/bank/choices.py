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
    BIC_SWIFT = ChoiceItem('bic_swift', _('BIC/SWIFT'))
    ACCOUNT_NUMBER = ChoiceItem('accountNumber', _('Account Number'))


class BankAccountType(DjangoChoices):
    """
    Choices for bank account types.
    """
    CHECKING = ChoiceItem('checking', _('Checking Account'))
    SAVINGS = ChoiceItem('savings', _('Savings Account'))
