# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-27 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20171227_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalinvoice',
            name='template',
            field=models.CharField(choices=[('default', 'Default'), ('without_bank_account', 'Without Bank Account')], default='default', help_text='The template to use to generate this invoice.', max_length=80),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='template',
            field=models.CharField(choices=[('default', 'Default'), ('without_bank_account', 'Without Bank Account')], default='default', help_text='The template to use to generate this invoice.', max_length=80),
        ),
    ]
