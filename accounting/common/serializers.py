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
Serializers used by multiple applications in the Accounting service.
"""

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


class UuidRelatedField(SlugRelatedField):
    """
    A `SlugRelatedField` whose `slug_field` is the `uuid` field by default.
    """

    def __init__(self, slug_field='uuid', **kwargs):
        super().__init__(slug_field=slug_field, **kwargs)


class UuidModelSerializer(serializers.ModelSerializer):
    """
    `ModelSerializer` which has a UUID field by default.
    """

    uuid = serializers.ReadOnlyField()

    class Meta:
        fields = ('uuid',)
