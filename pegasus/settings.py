"""
Django settings for pegasus project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


load_dotenv()


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
    'pegasus',
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

ROOT_URLCONF = 'pegasus.urls'

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
        'ENGINE': 'olympus.db.backends.postgresql',
        'OPTIONS': {'sslmode': os.getenv('DATABASE_SSLMODE', 'require')},
        'NAME': os.getenv('DATABASE_NAME', 'pegasus'),
        'USER': os.getenv('DATABASE_USER', 'pegasus'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'pegasus'),
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

AUTH_USER_MODEL = 'pegasus.User'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'hashers_passlib.pbkdf2_sha512',
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'pegasus.auth.backends.UserOTPBackend']

AUTH_TOKEN_LENGTH = os.getenv('AUTH_TOKEN_LENGTH', 64)
AUTH_TOKEN_VALIDITY = os.getenv('AUTH_TOKEN_VALIDITY', 3600)
AUTH_TOKEN_CREATE_NEW_THRESHOLD = os.getenv('AUTH_TOKEN_CREATE_NEW_THRESHOLD', 300)

AUTH_PIN_LENGTH = os.getenv('AUTH_PIN_LENGTH', 8)
AUTH_PIN_VALIDITY = os.getenv('AUTH_PIN_VALIDITY', 600)
AUTH_PIN_CREATE_NEW_THRESHOLD = os.getenv('AUTH_PIN_CREATE_NEW_THRESHOLD', 300)

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
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


# JWT
JWT_ISSUER = os.getenv('JWT_ISSUER')
JWT_PRIVATE_KEY = os.getenv('JWT_PRIVATE_KEY')
JWT_PUBLIC_KEY = os.getenv('JWT_PUBLIC_KEY')


# Messaging
BROKER_URL = os.getenv('BROKER_URL')


# Sentry Integration

sentry_sdk.init(
    environment='development' if DEBUG else os.getenv('SENTRY_ENVIRONMENT', 'production'),
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=os.getenv('SENTRY_TRACES_SAMPLE_RATE', 1.0),
    send_default_pii=True,
)
