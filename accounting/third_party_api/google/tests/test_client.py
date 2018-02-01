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
Tests for the  Google API client.
"""

from unittest import mock

from accounting.common.tests.base import TestCase
from accounting.third_party_api.google.client import GoogleDrive


class GoogleDriveTestCase(TestCase):
    """
    Test cases for the Google Drive client.
    """

    def setUp(self):
        """Set up test objects."""
        super().setUp()
        self.google_drive = GoogleDrive()
        self.path = ['non-existent-folder', '2018', 'invoices-in', '01']

        # Set up mocks.
        get_list_mock = mock.patch('pydrive.apiattr.ApiResourceList.GetList')
        self.get_list_mock = get_list_mock.start()
        self.addCleanup(get_list_mock.stop)

    def test_get_folder_id(self):
        """The ID of the folder at the end of the path."""
        self.get_list_mock.side_effect = [
            [],
            [{'title': '2017', 'id': None}, {'title': '2018', 'id': None}],
            [{'title': 'invoices-in', 'id': None}, {'title': 'invoices-out', 'id': None}],
            [{'title': '01', 'id': 'expected_id'}],
        ]
        folder_id = self.google_drive.get_folder_id('id', path=self.path)
        self.assertEqual(folder_id, 'expected_id')

    def test_get_folder_id_no_path(self):
        """If no path is given, we just return the root."""
        self.assertEqual(self.google_drive.get_folder_id('root'), 'root')

    def test_get_folder_id_path_not_list(self):
        """If `path` is not a list, we just return the root."""
        self.assertEqual(self.google_drive.get_folder_id('root', path='path'), 'root')
