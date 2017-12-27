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
Address models.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from accounting.common.models import UuidModel


class Address(UuidModel):
    """
    An address holding generic locational information.
    """

    country = CountryField(
        help_text=_("The country associated with this user account."))
    address_line1 = models.CharField(
        max_length=128,
        help_text=_("The first address line to appear on accounting documents, i.e. invoices."))
    address_line2 = models.CharField(
        max_length=128, blank=True, null=True,
        help_text=_("Additional line for extending an address."))
    zipcode = models.CharField(
        max_length=10,
        help_text=_("A 5-digit or ZIP+4 zipcode. Example: 12345, 12345-6789."))
    city = models.CharField(
        max_length=60,
        help_text=_("The city associated with this user account."))
    state = models.CharField(
        max_length=80, blank=True, null=True,
        help_text=_("The state or province associated with this user account. "
                    "Required if country is US, CA, AU, or BR."))

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        """
        Return a string identifying this address object.
        """
        return (
            '{address_line1}{optional_space1}{address_line2}, '
            '{city}{optional_space2}{state} {zipcode}, '
            '{country}'.format(
                address_line1=self.address_line1,
                optional_space1=' ' if self.address_line2 else '',
                address_line2=self.address_line2 or '',
                city=self.city,
                optional_space2=' ' if self.state else '',
                state=self.state or '',
                zipcode=self.zipcode,
                country=self.country,
            )
        )

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """
        Strip address lines of newlines.
        """
        self.address_line1 = self.address_line1.replace('\n', ' ')
        self.address_line2 = self.address_line2.replace('\n', ' ') if self.address_line2 else ''
        super().save(*args, **kwargs)
