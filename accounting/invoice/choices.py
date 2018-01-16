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

from django.utils.translation import ugettext_lazy as _
from djchoices import ChoiceItem, DjangoChoices


class InvoiceTemplate(DjangoChoices):
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
