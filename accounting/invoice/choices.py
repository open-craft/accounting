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
Invoice choices.
"""

import datetime

from django.utils.translation import ugettext_lazy as _
from djchoices import ChoiceItem, DjangoChoices


class InvoiceHtmlTemplate(DjangoChoices):
    """
    Choices for which invoice template to use.

    If adding a new template, make sure the directory & HTML/CSS file names match the choice name.

    For example, if adding a new invoice template 'stylish', name the files 'stylish.html' and 'stylish.css'
    in directory 'stylish'.

    By default, the `default/default.html` template is used, with styles `default/css/default.css`.
    """

    Default = ChoiceItem('default', _('Default'))


class InvoiceApproval(DjangoChoices):
    """
    Choices for how an invoice can be approved, including whether it is approved or not.
    """

    automatically = ChoiceItem('automatically', _('Automatically'))
    manually = ChoiceItem('manually', _('Manually'))
    not_approved = ChoiceItem('not_approved', _('Not Approved'))

    @classmethod
    def approved_choices(cls):
        """ The list of choices which count as being approved. """
        return [cls.automatically, cls.manually]

    @classmethod
    def not_approved_choices(cls):
        """ The list of choices which count as not being approved. """
        return [cls.not_approved]


class InvoiceNumberingScheme(DjangoChoices):
    """
    Different numbering schemes that can be used in an invoice.

    For each choice C there exists a method `increment_C` that knows how to increment that choice's numbering scheme.
    """

    default = ChoiceItem('%Y-%m', _('yyyy-mm (2018-01)'))
    number = ChoiceItem('{number}', _('{number} (42, for the 42nd invoice)'))
    year_month_number = ChoiceItem('%Y-%m-{number}', _('yyyy-mm-{number} (2018-01-42, for the 42nd invoice)'))
    year_month_one = ChoiceItem('%Y-%m-01', _('yyyy-mm-01 (2018-01-01, 2018-02-01 etc.)'))
    opencraft_year_month = ChoiceItem('OC-%Y-%m', _('OC-yyyy-mm (OC-2018-01)'))
    opencraft_number = ChoiceItem('OC-{number}', _('OC-{number} (OC-42, for the 42nd invoice)'))

    @classmethod
    def default_default(cls):
        """
        Return the default value given to the `default` choice.

        Arguably not the best name ever thought of, but necessary for consistency.
        """
        return datetime.datetime.now().strftime(cls.default)

    @classmethod
    def default_number(cls):
        """
        Return the default value given to the `number` choice.
        """
        return cls.number.format(number=1)

    @classmethod
    def default_year_month_number(cls):
        """
        Return the default value given to the `year_month_number` choice.
        """
        return '{}-{}'.format(cls.default_default(), cls.default_number())

    @classmethod
    def default_year_month_one(cls):
        """
        Return the default value given to the `year_month_one` choice.
        """
        return '{}-01'.format(cls.default_default())

    @classmethod
    def default_opencraft_year_month(cls):
        """
        Return the default value given to the `year_month` choice.
        """
        return 'OC-{}'.format(cls.default_default())

    @classmethod
    def default_opencraft_number(cls):
        """
        Return the default value given to the `opencraft_number` choice.
        """
        return 'OC-{}'.format(cls.default_number())

    @classmethod
    def default_value(cls, numbering_scheme):
        """
        Get the default value of any passed in numbering scheme.

        Assumes:
        * `numbering_scheme` is one of the value strings associated with a choice, not the `ChoiceItem` object.
        """
        function_name = cls.attributes[numbering_scheme]
        function = getattr(InvoiceNumberingScheme, 'default_{}'.format(function_name))
        return function()

    @classmethod
    def increment_default(cls, value):
        """
        Increment the number for the 'default' numbering scheme.

        Assumes `value` is in the format of the 'default' numbering scheme.
        """
        # Turn the input value string into a datetime object.
        datetime_obj = datetime.datetime.strptime(value, cls.default)
        # Increment it one month forward.
        incremented_obj = datetime_obj + datetime.timedelta(days=32)
        # Turn the object back into a string using the numbering scheme.
        return incremented_obj.strftime(cls.default)

    @classmethod
    def increment_number(cls, value):
        """
        Increment the number for the 'number' numbering scheme.

        Assumes `value` is in the format of the 'number' numbering scheme.
        """
        return cls.number.format(number=int(value) + 1)

    @classmethod
    def increment_year_month_number(cls, value):
        """
        Increment the number for the 'year_month_number' numbering scheme.

        Assumes `value` is in the format of the 'year_month_number' numbering scheme.
        """
        date, number = value.rsplit('-', 1)
        incremented_date = cls.increment_default(date)
        incremented_number = cls.increment_number(number)
        return '-'.join([incremented_date, incremented_number])

    @classmethod
    def increment_year_month_one(cls, value):
        """
        Increment the number for the 'year_month_one' numbering scheme.

        Assumes `value` is in the format of the 'year_month_one' numbering scheme.
        """
        date, _ = value.rsplit('-', 1)
        incremented_date = cls.increment_default(date)
        return '{}-01'.format(incremented_date)

    @classmethod
    def increment_opencraft_year_month(cls, value):
        """
        Increment the number for the 'opencraft_year_month' numbering scheme.

        Assumes `value` is in the format of the 'opencraft_year_month' numbering scheme.
        """
        prefix, date = value.split('-', 1)
        incremented_date = cls.increment_default(date)
        return '-'.join([prefix, incremented_date])

    @classmethod
    def increment_opencraft_number(cls, value):
        """
        Increment the number for the 'opencraft_number' numbering scheme.

        Assumes `value` is in the format of the 'opencraft_number' numbering scheme.
        """
        prefix, number = value.split('-', 1)
        incremented_number = cls.increment_number(number)
        return '-'.join([prefix, incremented_number])

    @classmethod
    def increment_value(cls, numbering_scheme, value):
        """
        Increment any passed in value given its matching numbering scheme choice.

        Assumes:
        * `numbering_scheme` is one of the value strings associated with a choice, not the `ChoiceItem` object.
        * `value` is in the format of the choice's numbering scheme.
        """
        function_name = cls.attributes[numbering_scheme]
        function = getattr(InvoiceNumberingScheme, 'increment_{}'.format(function_name))
        return function(value)
