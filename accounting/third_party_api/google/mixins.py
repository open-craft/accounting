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
Google mixins to be used by the Accounting service.
"""

from django.conf import settings

from accounting.third_party_api.google.auth import GoogleAuth
from accounting.third_party_api.google.client import GoogleDrive


class GoogleDriveMixin:
    """
    Mixin for common Google Drive functionality.
    """

    def upload_to_google_drive(self, file_path=None, target_path=None, title=None):  # NOQA
        """
        Upload a file to Google Drive.

        You can specify an arbitrary target path, given `settings.GOOGLE_DRIVE_ROOT`. For example:
            |- 2016
            |- 2017
            |   |- blah
            |   |- ...
            |   |- invoices-in
            |   |   |- 1
            |   |   |- 2
            |   |   |- ...
            |   |   |- 12
            |   |   |   |- invoice_1.pdf
            |   |   |   |- ...
            |   |   |   |- invoice_new_n-1.pdf
            |   |   |   |- invoice_n.pdf
            |- 2018

        The above is a potential folder structure, where the variables could be:

        >>> self.upload_to_google_drive(
        >>>     file_path='/var/www/media/invoice.pdf',
        >>>     target_path=['2017', 'invoices-in', '12'],
        >>>     title='invoice_new-n-1.pdf',
        >>> )

        Requires `settings.ENABLE_GOOGLE` to be turned on.

        TODO: This should be a synchronous job on a non-web worker.
        """
        if not settings.ENABLE_GOOGLE:
            return

        gauth = GoogleAuth()
        gauth.ServiceAuth()
        drive = GoogleDrive(gauth)
        target_folder = drive.get_folder_id(settings.GOOGLE_DRIVE_ROOT, path=target_path)
        file = drive.CreateFile({'title': title, 'parents': [{'id': target_folder}]})
        file.SetContentFile(file_path)
        file.Upload()
        return file
