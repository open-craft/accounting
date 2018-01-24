# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-23 11:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0008_invoice_templates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicetemplate',
            name='extra_text',
            field=models.TextField(blank=True, help_text='Any arbitrary extra text that the provider would like to display on their invoice. The HTML template that belongs to this invoice template should have a designated location to place this extra text.', null=True),
        ),
    ]
