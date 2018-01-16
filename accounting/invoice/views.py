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
Invoice views.
"""

from rest_framework import decorators, permissions, response, viewsets

from accounting.invoice import choices, models


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    A view for retrieving and updating `Invoice` objects.
    """

    permission_classes = (permissions.IsAdminUser,)
    queryset = models.Invoice.objects.all()
    lookup_field = 'uuid'

    @decorators.detail_route(
        permission_classes=[permissions.AllowAny],
        queryset=models.Invoice.objects.filter(approved=choices.InvoiceApproval.not_approved)
    )
    def approve(self, request, uuid=None):
        """
        Approve the invoice with UUID `uuid`.
        """
        invoice = self.get_object()
        invoice.approved = choices.InvoiceApproval.manually
        invoice.save()
        return response.Response({'approved': True})

    @decorators.detail_route(queryset=models.Invoice.objects.filter(paid=False))
    def pay(self, request, uuid=None):
        """
        Pay the invoice with UUID `uuid`.
        """
        invoice = self.get_object()
        invoice.paid = True
        invoice.save()
        return response.Response({
            'paid': True,
            'total': invoice.total_cost,
            'currency': invoice.hourly_rate.hourly_rate_currency
        })
