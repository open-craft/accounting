# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-24 16:57
from __future__ import unicode_literals

import uuid

from django.db import migrations, models
import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The universally unique identifier for this model instance.', verbose_name='UUID')),
                ('name', models.CharField(help_text='The official name of the bank.', max_length=80)),
                ('address', models.ForeignKey(blank=True, help_text='The address of this bank.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='banks', to='address.Address')),
            ],
            options={
                'verbose_name': 'Bank',
                'verbose_name_plural': 'Banks',
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The universally unique identifier for this model instance.', verbose_name='UUID')),
                ('currency', djmoney.models.fields.CurrencyField(default='EUR', help_text='The currency expected to be held in this bank account.', max_length=3)),
                ('type', models.CharField(choices=[('checking', 'Checking Account'), ('savings', 'Savings Account')], help_text='Whether this is a checking or savings account.', max_length=30)),
                ('identification', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={'abartn': '', 'accountNumber': '', 'bankCode': '', 'bankgiroNumber': '', 'bic': '', 'branchCode': '', 'bsbCode': '', 'cardNumber': '', 'clabe': '', 'iban': '', 'ifscCode': '', 'institutionNumber': '', 'routingNumber': '', 'sortCode': '', 'swiftCode': '', 'transitNumber': ''}, help_text='The unique combination of identification information for this bank account.')),
                ('bank', models.ForeignKey(help_text='The bank to which this bank account belongs.', on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to='bank.Bank')),
                ('user_account', models.ForeignKey(help_text='The user account that this bank account is linked to. A user can have multiple bank accounts associated with their user account.', on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to='account.Account')),
            ],
            options={
                'verbose_name': 'Bank Account',
                'verbose_name_plural': 'Bank Accounts',
            },
        ),
    ]
