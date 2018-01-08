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

from datetime import timedelta

from django.utils import timezone


def get_last_day_past_month():
    """
    Return the `datetime` object representing the last day of the month that just passed.
    """
    return timezone.now().replace(day=1) - timedelta(days=1)


def get_first_day_past_month():
    """
    Return the `datetime` object representing the first day of the month that just passed.
    """
    return get_last_day_past_month().replace(day=1)


def default_invoice_number():
    """
    Return the invoice number which defaults to `yyyy-mm` for the current year and month.
    """
    return timezone.now().strftime("%Y-%m")
