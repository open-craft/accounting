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
Google API Auth to be used by the Accounting service.
"""

from django.conf import settings
from pydrive.auth import GoogleAuth as UpstreamGoogleAuth


class GoogleAuth(UpstreamGoogleAuth):
    """
    An override of upstream `GoogleAuth` to allow using Django settings for certain default configuration.
    """

    # Override upstream default settings to use Django defaults for service configuration.
    DEFAULT_SETTINGS = {
        'client_config_backend': 'service',
        'service_config': {
            'client_user_email': settings.GOOGLE_AUTH_CLIENT_USER_EMAIL,
            'client_service_email': settings.GOOGLE_AUTH_CLIENT_SERVICE_EMAIL,
            'client_pkcs12_file_path': settings.GOOGLE_AUTH_PKCS12_FILE_PATH,
        },
        'save_credentials': False,
        'oauth_scope': ['https://www.googleapis.com/auth/drive']
    }
