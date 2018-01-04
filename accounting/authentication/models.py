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
Authentication models.
"""

from django.contrib.auth import models
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _

from accounting.common.models import CommonModel, UuidModel


class User(CommonModel, UuidModel, models.AbstractUser):
    """
    A `User` model with custom columns, like `uuid` and `full_name`.
    """

    full_name = CharField(
        max_length=255, blank=True, null=True,
        help_text=_("The full name of this user."))

    def get_full_name(self):
        """
        Gets the full name of this user, whether that's through `full_name` or `first_name` and `last_name`.
        """
        return self.full_name or super().get_full_name()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
