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
Base classes for test classes throughout the Accounting service.
"""

from django.test import TestCase as DjangoTestCase

from accounting.invoice.models import Invoice


class TestCase(DjangoTestCase):
    """ Common test case for test classes throughout the Accounting service. """

    def tearDown(self):
        """ Delete any leftover files. """
        for invoice in Invoice.objects.all():
            invoice.extra_image.delete()
        super().tearDown()
