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
Common models used throughout the Accounting service.
"""

from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _


class UuidModel(models.Model):
    """
    A reusable model to allow storing UUIDs as a column.
    """

    uuid = models.UUIDField(
        blank=False, null=False, default=uuid4, editable=False, verbose_name=_("UUID"),
        help_text=_("The universally unique identifier for this model instance."))

    class Meta:
        abstract = True
