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

# pylint: disable=attribute-defined-outside-init
"""
Factories for testing the Account application.
"""

import factory

from accounting.authentication import models
from accounting.common.tests.factories import UuidFactory


class UserFactory(UuidFactory):
    """ Factory for `models.User`. """

    username = factory.Faker('user_name')
    password = 'password'
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = models.User

    @factory.post_generation
    def set_full_name(self, create, extracted, **kwargs):
        """
        Let the user's `full_name` be a combination of `first_name` and `last_name`.
        """
        self.full_name = '{} {}'.format(self.first_name, self.last_name)
        self.save()
