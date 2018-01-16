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
Invoice choices tests.
"""

from accounting.common.tests.base import TestCase
from accounting.invoice import choices


class InvoicePreparationNotificationTestCase(TestCase):
    """ Test cases for `tasks.send_invoice_prep_notification`. """

    def test_approved_choices(self):
        """ The approved choices list matches those choices that actually count as being approved. """
        self.assertEqual(choices.InvoiceApproval.approved_choices(), ['automatically', 'manually'])

    def test_not_approved_choices(self):
        """ The not-approved choices list matches those choices that actually aren't counted as being approved. """
        self.assertEqual(choices.InvoiceApproval.not_approved_choices(), ['not_approved'])
