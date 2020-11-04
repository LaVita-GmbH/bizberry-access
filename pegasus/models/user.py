from datetime import datetime, timedelta
from jose import jwt
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager as BaseUserManager
from djutils.crypt import random_string_generator


def _default_user_id():
    return random_string_generator(size=64)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if extra_fields.get('id'):
            raise ValueError('The ID cannot be given on creation')

        elif 'id' in extra_fields:
            del extra_fields['id']

        email = email and self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        TERMINATED = 'terminated', _('Terminated')

    id = models.CharField(max_length=64, primary_key=True, default=_default_user_id, editable=False)
    email = models.CharField(max_length=320, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    first_name = None
    last_name = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def username(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @is_active.setter
    def is_active(self, value: bool):
        if value is True:
            self.status = self.Status.ACTIVE

        else:
            self.status = self.Status.TERMINATED

    def clean(self):
        pass

    def create_transaction_token(self):
        time_now = datetime.now()
        time_expire = time_now + timedelta(minutes=5)
        claims = {
            'iss': settings.JWT_ISSUER,
            'iat': time_now,
            'exp': time_expire,
            'sub': self.id,
            'aud': [],
        }

        token = jwt.encode(
            claims=claims,
            key=settings.JWT_PRIVATE_KEY,
            algorithm='ES512',
        )

        return token
