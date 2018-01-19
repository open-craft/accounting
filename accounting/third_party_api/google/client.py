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
Google API Client to be used by the Accounting service.
"""

from pydrive.drive import GoogleDrive as UpstreamGoogleDrive


class GoogleDrive(UpstreamGoogleDrive):
    """
    An override of the upstream Google Drive to provide additional functionality.
    """

    # A query for finding a folder.
    FOLDER_QUERY = ("mimeType ='application/vnd.google-apps.folder' and "
                    "'{parent}' in parents and "
                    "trashed=false")

    def get_folder_id(self, root, path=None):
        """
        Return the ID of the folder with the last name in `path`, starting traversal from folder given by ID `root`.
        """
        if path and isinstance(path, list):
            folders = self.ListFile({'q': self.FOLDER_QUERY.format(parent=root)}).GetList()
            for folder in folders:
                if folder['title'] == path[0]:
                    root = folder['id']
                    break
            return self.get_folder_id(root, path[1:])
        return root
