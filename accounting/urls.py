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
Accounting URL Configuration.
"""

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from accounting.invoice.urls import router as invoice_router

urlpatterns = [
    url(r'^', include(invoice_router.urls, namespace='invoice')),
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('accounting.account.urls', namespace='account')),
    url(r'^address/', include('accounting.address.urls', namespace='address')),
    url(r'^auth/', include('accounting.authentication.urls', namespace='auth')),
    url(r'^bank/', include('accounting.bank.urls', namespace='bank')),
    url(r'^registration/', include('accounting.registration.urls', namespace='registration')),
    url(r'^third_party/', include('accounting.third_party_api.urls', namespace='third_party')),
    url(r'^transferwise/', include('accounting.transferwise.urls', namespace='transferwise')),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.ENABLE_DEBUG_TOOLBAR:
        import debug_toolbar
        # "debug" URL pattern must be before "site" URL pattern.
        # See https://github.com/jazzband/django-debug-toolbar/issues/529
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls, namespace='debug')),
        ]
