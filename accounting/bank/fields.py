# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2017 OpenCraft <contact@opencraft.com>
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
Bank fields used by any of the Bank models.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _


class AUBankStateBranchField(models.CharField):
    """
    A model field that checks that the value is a valid Australian Bank State Branch (BSB) code.

    BSBs are 6-digit codes. From https://www.thebsbnumbers.com/:
        - The First two digits (XX) specify the parent financial institution.
        - Third digit (Y) specifies the state where the branch is located.
        - Fourth, fifth and sixth digits (ZZZ) specify the branch location.
    """

    description = _("Australian Bank State Branch")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 6
        super(AUBankStateBranchField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Ensure the BSB code is stored without dashes."""
        value = super(AUBankStateBranchField, self).to_python(value)

        if value is not None:
            return ''.join(value.split('-'))

        return value
