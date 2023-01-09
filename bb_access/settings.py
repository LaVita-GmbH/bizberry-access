"""
Django settings for bb_access project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import json
from base64 import b64decode
from tempfile import NamedTemporaryFile
from pathlib import Path
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


load_dotenv()


APP_NAME = 'BB Access'
APP_VERSION = '0.0.1'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 't#4w_p3jg=61)r3y$e95eyl46lkb+#_-ifas@&$9hm_ko_lo9o')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv('DEBUG') else False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'bb_access',
    'health_check',
    'health_check.db',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bb_access.urls'

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


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.postgresql'),
        'CONN_MAX_AGE': 0,
        'OPTIONS': {
            'sslmode': os.getenv('DATABASE_SSLMODE', 'require'),
        },
        'NAME': os.getenv('DATABASE_NAME', 'bb_access'),
        'USER': os.getenv('DATABASE_USER', 'bb_access'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'bb_access'),
        'HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

CSRF_TRUSTED_ORIGINS = [origin for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin]

AUTH_USER_MODEL = 'bb_access.User'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'bb_access.auth.backends.UserOTPBackend']

AUTH_TOKEN_LENGTH = int(os.getenv('AUTH_TOKEN_LENGTH', 64))
AUTH_TOKEN_VALIDITY = int(os.getenv('AUTH_TOKEN_VALIDITY', 3600 * 4))
AUTH_TOKEN_CREATE_NEW_THRESHOLD = int(os.getenv('AUTH_TOKEN_CREATE_NEW_THRESHOLD', 300))
AUTH_TOKEN_CRITICAL_THRESHOLD = int(os.getenv('AUTH_TOKEN_CRITICAL_THRESHOLD', 3600))

AUTH_PIN_LENGTH = os.getenv('AUTH_PIN_LENGTH', 8)
AUTH_PIN_VALIDITY = os.getenv('AUTH_PIN_VALIDITY', 600)
AUTH_PIN_CREATE_NEW_THRESHOLD = int(os.getenv('AUTH_PIN_CREATE_NEW_THRESHOLD', 300))

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOGLEVEL', 'INFO'),
    },
}


# JWT
JWT_ISSUER = os.getenv('JWT_ISSUER')
JWT_PRIVATE_KEY = os.getenv('JWT_PRIVATE_KEY')
JWT_PUBLIC_KEY = os.getenv('JWT_PUBLIC_KEY')


# Messaging
BROKER_URL = os.getenv('BROKER_URL')
BROKER_ACKS = {'0': 0, '1': 1, 'all': 'all'}[os.getenv('BROKER_ACKS', 'all')]
BROKER_REQUEST_TIMEOUT = os.getenv('BROKER_REQUEST_TIMEOUT', 30000)
BROKER_SESSION_TIMEOUT = os.getenv('BROKER_SESSION_TIMEOUT', 10000)
BROKER_SECURITY_PROTOCOL = os.getenv('BROKER_SECURITY_PROTOCOL', 'PLAINTEXT')
BROKER_SASL_MECHANISM = os.getenv('BROKER_SASL_MECHANISM')
BROKER_SASL_PLAIN_USERNAME = os.getenv('BROKER_SASL_PLAIN_USERNAME')
BROKER_SASL_PLAIN_PASSWORD = os.getenv('BROKER_SASL_PLAIN_PASSWORD')
with NamedTemporaryFile(delete=False) as _tempfile:
    _tempfile.write(b64decode(os.getenv('BROKER_SSL_CERT', '')))

BROKER_SSL_CERTFILE = _tempfile.name


# Sentry Integration

def sentry_traces_sampler(context):
    if 'asgi_scope' in context and context['asgi_scope']['path'] == '/':
        return 0

    return float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', 1.0))


sentry_sdk.init(
    environment='development' if DEBUG else os.getenv('SENTRY_ENVIRONMENT', 'production'),
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sampler=sentry_traces_sampler,
    send_default_pii=True,
)

# Sender
SENDER_EMAIL_INTEGRATION = os.getenv('SENDER_EMAIL_INTEGRATION', 'SMTP')
SENDER_EMAIL_INTEGRATION_SMTP_HOST = os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_HOST', None)
SENDER_EMAIL_INTEGRATION_SMTP_PORT = int(os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_PORT', 25))
SENDER_EMAIL_INTEGRATION_SMTP_USE_SSL = bool(os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_USE_SSL', False))
SENDER_EMAIL_INTEGRATION_SMTP_USE_STARTTLS = bool(os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_USE_STARTTLS', False))
SENDER_EMAIL_INTEGRATION_SMTP_USER = os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_USER', None)
SENDER_EMAIL_INTEGRATION_SMTP_PASSWORD = os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_PASSWORD', None)
SENDER_EMAIL_INTEGRATION_SMTP_TIMEOUT = os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_TIMEOUT', 10)
SENDER_EMAIL_INTEGRATION_SMTP_SENDER_NAME = os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_SENDER_NAME', None)
SENDER_EMAIL_INTEGRATION_SMTP_SENDER_EMAIL = os.getenv('SENDER_EMAIL_INTEGRATION_SMTP_SENDER_EMAIL', None)

SENDER_SMS_INTEGRATION = os.getenv('SENDER_SMS_INTEGRATION', None)
SENDER_SMS_INTEGRATION_MAILJET_SENDER_NAME = os.getenv('SENDER_SMS_INTEGRATION_MAILJET_SENDER_NAME', None)
SENDER_SMS_INTEGRATION_MAILJET_TOKEN = os.getenv('SENDER_SMS_INTEGRATION_MAILJET_TOKEN', None)


# Other
EMAIL_CHECK_SMTP_HELO_HOST = os.getenv('EMAIL_CHECK_SMTP_HELO_HOST')

WEBSITE_URL = os.getenv('WEBSITE_URL', 'http://localhost')
WEBSITE_SHOP_URL = os.getenv('WEBSITE_SHOP_URL', 'http://localhost')
WEBSITE_ASSETS_URL = os.getenv('WEBSITE_ASSETS_URL', 'http://localhost')
WEBSITE_BUSINESS_URL = os.getenv('WEBSITE_BUSINESS_URL', 'http://localhost')
WEBSITE_BUSINESS_EMAIL = os.getenv('WEBSITE_BUSINESS_EMAIL', 'http://localhost')

TEMPLATE_GLOBALS = {
    'website_url': WEBSITE_URL,
    'website_shop_url': WEBSITE_SHOP_URL,
    'website_assets_url': WEBSITE_ASSETS_URL,
    'website_business_url': WEBSITE_BUSINESS_URL,
    'website_business_email': WEBSITE_BUSINESS_EMAIL,
}
