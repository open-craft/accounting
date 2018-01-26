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
Django settings for the Accounting Automation project.

See `.environ/.env.dev` for details on certain settings needed for a development environment,
and for the most part a production environment.
"""

from urllib.parse import urlparse
import logging
import os

import environ

env = environ.Env()
root = environ.Path(os.path.dirname(__file__), os.pardir)
environ.Env.read_env(root('.env'))

SITE_ROOT = root()

# Security ####################################################################

SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=True)

ENABLE_DEBUG_TOOLBAR = env.bool('ENABLE_DEBUG_TOOLBAR', default=DEBUG)

ALLOWED_HOSTS = env.json('ALLOWED_HOSTS', default=[])

# Application #################################################################

LOCAL_APPS = (
    'accounting.account',
    'accounting.address',
    'accounting.authentication',
    'accounting.bank',
    'accounting.common',
    'accounting.invoice',
    'accounting.registration',
    'accounting.third_party_api',
    'accounting.transferwise',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_countries',
    'django_extensions',
    'djmoney',
    'huey.contrib.djhuey',
    'rangefilter',
    'rest_framework',
    'rest_framework.authtoken',
    'simple_email_confirmation',
    'simple_history',
    'taggit',
    'vies',
) + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

if DEBUG and ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda request: True}

ROOT_URLCONF = 'accounting.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'accounting.wsgi.application'

SITE_ID = env('SITE_ID', default=1)

# Database ####################################################################

# Set via the environment variable `DATABASE_URL`
DATABASES = {
    'default': env.db(),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework (APIs, Auth) #################################################

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour',
        'anon': '50/hour',
    },
}

# Internationalization ########################################################

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (
    root('accounting/conf/locale'),
)

# Static files (CSS, JavaScript, Images) ######################################

STATIC_URL = '/static/'
STATIC_ROOT = root('static')
STATICFILES_DIRS = (
    root('accounting/static'),
)

# Media (File Uploads) ########################################################

MEDIA_URL = '/media/'
MEDIA_ROOT = root('media')

# Authentication ##############################################################

AUTH_USER_MODEL = 'authentication.User'

# Django-extensions ###########################################################

SHELL_PLUS = "ipython"
RUNSERVERPLUS_SERVER_ADDRESS_PORT = env('RUNDEV_SERVER_ADDRESS_PORT', default='0.0.0.0:1786')

# Redis cache & locking #######################################################

REDIS_LOCK_TIMEOUT = env('REDIS_LOCK_TIMEOUT', default=900)
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/')
REDIS_URL_OBJ = urlparse(REDIS_URL)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Huey (redis task queue) #####################################################

HUEY = {
    'name': env('HUEY_QUEUE_NAME', default='accounting'),
    'connection': {
        'host': REDIS_URL_OBJ.hostname,
        'port': REDIS_URL_OBJ.port,
        'password': REDIS_URL_OBJ.password,
    },
    'always_eager': env.bool('HUEY_ALWAYS_EAGER', default=False),

    # Options to pass into the consumer when running ``manage.py run_huey``
    'consumer': {'workers': 1, 'loglevel': logging.DEBUG},
}

# Emails ######################################################################

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# From & subject configuration for sent emails
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='accounting@localhost')
SERVER_EMAIL = env('SERVER_EMAIL', default='accounting@locahost')
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='[OpenCraft Accounting] ')

# SMTP configuration
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env('EMAIL_PORT', default=25)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# Email confirmation
SIMPLE_EMAIL_CONFIRMATION_AUTO_ADD = False

ADMINS = env.json('ADMINS', default=set())

# LOGGING #####################################################################

BASE_HANDLERS = env.json('BASE_HANDLERS', default=["file", "accounting", "mail_admins"])
HANDLERS = BASE_HANDLERS
LOGGING_ROTATE_MAX_KBYTES = env.json('LOGGING_ROTATE_MAX_KBYTES', default=10 * 1024)
LOGGING_ROTATE_MAX_FILES = env.json('LOGGING_ROTATE_MAX_FILES', default=60)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "{asctime} | {levelname:>8.8s} | process={process:<5d} | {name:<25.25s} | {message}",
            'style': '{',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'db': {
            'format': "{name:<25.25s} | {message}",
            'style': '{',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'accounting': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': HANDLERS,
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': HANDLERS,
            'propagate': False,
            'level': 'INFO',
        },
        'accounting': {
            'handlers': HANDLERS,
            'propagate': False,
            'level': 'DEBUG',
        },
        'requests': {
            'handlers': HANDLERS,
            'propagate': False,
            'level': 'DEBUG',
        },
        'requests.packages.urllib3': {
            'handlers': HANDLERS,
            'propagate': False,
            'level': 'WARNING',
        }
    }
}

if 'file' in HANDLERS:
    LOGGING['handlers']['file'] = {
        'level': 'DEBUG',
        'class': 'accounting.common.logging.GzipRotatingFileHandler',
        'filename': 'log/accounting.{}.log'.format(env('HONCHO_PROCESS_NAME', default='main')),
        'maxBytes': LOGGING_ROTATE_MAX_KBYTES * 1024,
        'backupCount': LOGGING_ROTATE_MAX_FILES,
        'formatter': 'verbose'
    }

# MONEY #######################################################################

DEFAULT_CURRENCY = 'EUR'

# JIRA ########################################################################

ENABLE_JIRA = env.bool('ENABLE_JIRA', default=False)
JIRA_SERVER_URL = env('JIRA_SERVER_URL', default='https://jira.atlassian.com')
JIRA_SERVICE_USER_USERNAME = env('JIRA_SERVICE_USER_USERNAME', default='')
JIRA_SERVICE_USER_PASSWORD = env('JIRA_SERVICE_USER_PASSWORD', default='')

# GOOGLE ######################################################################

ENABLE_GOOGLE = env.bool('ENABLE_GOOGLE', default=False)
GOOGLE_AUTH_CLIENT_USER_EMAIL = env('GOOGLE_AUTH_CLIENT_USER_EMAIL', default='')
GOOGLE_AUTH_CLIENT_SERVICE_EMAIL = env('GOOGLE_AUTH_CLIENT_SERVICE_EMAIL', default='')
GOOGLE_AUTH_PKCS12_FILE_PATH = env('GOOGLE_AUTH_PKCS12_FILE_PATH', default=root('.p12'))
GOOGLE_DRIVE_ROOT = env('GOOGLE_DRIVE_ROOT', default='')

# TRANSFERWISE ################################################################

TRANSFERWISE_BULK_PAYMENT_DAY = env('TRANSFERWISE_BULK_PAYMENT_DAY', default="6")
TRANSFERWISE_BULK_PAYMENT_SENDER = env('TRANSFERWISE_BULK_PAYMENT_SENDER', default='opencraft')

# HTML-to-PDF #################################################################

INVOICE_PDF_PATH = env('INVOICE_PDF_PATH', default=MEDIA_ROOT)
HTML_TO_PDF_BINARY_PATH = env('HTML_TO_PDF_BINARY_PATH', default=root('wkhtmltopdf'))

# BILLING CYCLE ###############################################################

BILLING_CYCLE_USERS = env.list('BILLING_CYCLE_USERS', default=['opencraft'])
INVOICE_NOTIFICATION_DAY = env('INVOICE_NOTIFICATION_DAY', default="1")
INVOICE_APPROVAL_DAY = env('INVOICE_APPROVAL_DAY', default="3")
INVOICE_FINAL_DAY = env('INVOICE_FINAL_DAY', default="5")
