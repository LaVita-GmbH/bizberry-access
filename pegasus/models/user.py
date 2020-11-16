from typing import List, Set, Tuple, Optional, Union
from datetime import datetime, timedelta
from jose import jwt
from asgiref.sync import sync_to_async
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.utils import timezone
from djutils.crypt import random_string_generator
from . import Scope, Role, Tenant


def _default_user_id():
    return random_string_generator(size=64)


def _default_user_token_id():
    return random_string_generator(size=128)


def _default_user_accesstoken_id():
    return random_string_generator(size=64)


def _default_user_accesstoken_token():
    return random_string_generator(size=128)


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
        ACTIVE = 'active', _("Active")
        TERMINATED = 'terminated', _("Terminated")

    class Type(models.TextChoices):
        USER = 'user', _("User")
        SERVICE = 'service', _("Service")

    id = models.CharField(max_length=64, primary_key=True, default=_default_user_id, editable=False)
    email = models.CharField(max_length=320, unique=True)
    password = models.CharField(_('password'), max_length=144)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    type = models.CharField(max_length=16, choices=Type.choices, default=Type.USER)
    roles = models.ManyToManyField(Role, related_name='users', blank=True, through='UserRoleRelation', through_fields=('user', 'role'),)

    first_name = None
    last_name = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def username(self) -> str:
        return self.email

    @property
    def is_staff(self) -> bool:
        return self.is_superuser

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE

    @is_active.setter
    def is_active(self, value: bool):
        if value is True:
            self.status = self.Status.ACTIVE

        else:
            self.status = self.Status.TERMINATED

    def clean(self):
        pass

    @sync_to_async
    def get_roles(self, tenant: Union[Tenant, str]) -> Set[Role]:
        if isinstance(tenant, str):
            tenant: Tenant = Tenant.objects.get(id=tenant)

        roles = set([rel.role for rel in self.roles_rel.filter(tenant=tenant)])
        if not roles and self.type == self.Type.USER:
            try:
                roles = {Role.objects.get(is_default_role=True)}

            except ObjectDoesNotExist:
                pass

        return roles

    async def get_scopes(self, tenant: Union[Tenant, str], include_critical: bool = True) -> Set[Scope]:
        scopes = set()
        for role in await self.get_roles(tenant=tenant):
            scopes.update(await role.get_scopes(include_critical=include_critical))

        return scopes

    @sync_to_async
    def _create_token(
        self,
        *,
        validity: timedelta,
        tenant: Union[Tenant, str],
        audiences: List[str] = [],
        store_in_db: bool = False,
        token_type: Optional['UserToken.Types'] = None,
    ) -> Tuple[str, str]:
        time_now = timezone.now()
        time_expire = time_now + validity

        token_id = random_string_generator(size=128)

        if isinstance(tenant, str):
            tenant: Tenant = Tenant.objects.get(id=tenant)

        claims = {
            'iss': settings.JWT_ISSUER,
            'iat': time_now,
            'nbf': time_now,
            'exp': time_expire,
            'sub': self.id,
            'ten': tenant.id,
            'aud': audiences,
            'jti': token_id,
        }

        token = jwt.encode(
            claims=claims,
            key=settings.JWT_PRIVATE_KEY,
            algorithm='ES512',
        )

        if store_in_db:
            self.tokens.create(id=token_id, tenant=tenant, type=token_type)

        return token, token_id

    async def create_transaction_token(self, tenant: Union[Tenant, str], include_critical: bool = False) -> str:
        audiences: List[str] = [scope.code for scope in await self.get_scopes(tenant=tenant, include_critical=include_critical)]

        token, _ = await self._create_token(
            validity=timedelta(minutes=5),
            tenant=tenant,
            audiences=audiences,
        )

        return token

    async def create_user_token(self, tenant: Union[Tenant, str]) -> str:
        token, token_id = await self._create_token(
            validity=timedelta(days=365),
            tenant=tenant,
            audiences=[
                'pegasus.users.request_transaction_token'
            ],
            store_in_db=True,
            token_type=UserToken.Types.USER,
        )

        return token


class UserRoleRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles_rel')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users_rel')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)


class UserToken(models.Model):
    class Types(models.TextChoices):
        USER = 'user', _('User Token')

    id = models.CharField(max_length=128, primary_key=True, default=_default_user_token_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_tokens')
    type = models.CharField(max_length=16, choices=Types.choices)
    create_date = models.DateTimeField(auto_now_add=True)


class UserAccessToken(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=_default_user_accesstoken_id, editable=False)
    token = models.CharField(max_length=128, unique=True, db_index=True, default=_default_user_accesstoken_token, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_tokens')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_access_tokens')
    last_used = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    scopes = models.ManyToManyField(Scope, related_name='user_access_tokens', limit_choices_to={'is_active': True, 'is_internal': False})

    @sync_to_async
    def get_scopes(self, include_critical: bool = True) -> Set[Scope]:
        filters = models.Q()
        if not include_critical:
            filters &= models.Q(is_critical=False)

        return set(self.scopes.filter(filters))

    async def create_transaction_token(self, include_critical: bool = False) -> str:
        scopes: Set[Scope] = await self.user.get_scopes()
        if self.scopes.count():
            scopes = scopes.intersection(await self.get_scopes(include_critical=include_critical))

        audiences: List[str] = [scope.code for scope in scopes]

        token, _ = await self.user._create_token(
            validity=timedelta(minutes=5),
            audiences=audiences,
            tenant=self.tenant,
        )

        return token
