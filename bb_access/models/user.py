import string
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from datetime import timedelta
from jose import jwt
from django.db import models
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin
from djpykafka.models import KafkaPublishMixin
from djutils.crypt import random_string_generator
from djdantic.schemas import Access, Error, AccessScope
from djfapi.exceptions import AuthError, ConstraintError
from djdantic import context
from . import Scope, Role, Tenant


def _default_user_id():
    return random_string_generator(size=64)


def _default_user_token_id():
    return random_string_generator(size=128)


def _default_user_accesstoken_id():
    return random_string_generator(size=64)


def _default_user_accesstoken_token():
    return random_string_generator(size=128)


def _default_user_otp_id():
    return random_string_generator(size=64)


def _default_user_flag_id():
    return random_string_generator(size=72)


class UserManager(BaseUserManager):
    @atomic
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

        if not user.has_usable_password():
            user.request_otp(
                type=UserOTP.UserOTPType.TOKEN,
            )

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(DirtyFieldsMixin, KafkaPublishMixin, AbstractUser):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _("Active")
        TERMINATED = 'TERMINATED', _("Terminated")

    class Type(models.TextChoices):
        USER = 'USER', _("User")
        SERVICE = 'SERVICE', _("Service")

    id = models.CharField(max_length=64, primary_key=True, default=_default_user_id, editable=False)
    tenant: Tenant = models.ForeignKey(Tenant, on_delete=models.RESTRICT, related_name='users')
    email: str = models.CharField(max_length=320, unique=False, db_index=True)
    number: Optional[str] = models.CharField(max_length=16, null=True, blank=True)
    password: str = models.CharField(_('password'), max_length=144)
    status: Status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    type: Type = models.CharField(max_length=16, choices=Type.choices, default=Type.USER)
    language: str = models.CharField(max_length=8)
    role: Optional[Role] = models.ForeignKey(Role, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    first_name: Optional[str] = models.CharField(max_length=150, blank=True, null=True)
    last_name: Optional[str] = models.CharField(max_length=150, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = [
        'email',
        'tenant_id',
        'language',
    ]

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

    @atomic
    def set_password(self, raw_password: Optional[str]) -> None:
        res = super().set_password(raw_password)
        token: UserToken
        for token in self.tokens.filter(is_active=True):
            token.is_active = False
            token.save()

        return res

    def get_role(self):
        return self.role or Role.objects.get(is_default=True)

    def get_scopes(self, include_critical: bool = True) -> Set[Scope]:
        role = self.get_role()
        
        return role.get_scopes(include_critical=include_critical)

    def get_roles(self) -> List[Role]:
        role = self.get_role()

        def _get_roles(role: Role, _excluded_role_ids: Optional[Set[id]] = None) -> Dict[Role, None]:
            roles = {role: None}
            if not _excluded_role_ids:
                _excluded_role_ids = set()
            _excluded_role_ids.add(role.id)

            for included_role in role.included_roles.exclude(id__in=_excluded_role_ids):
                _excluded_role_ids.add(included_role.id)
                roles.update(_get_roles(included_role, _excluded_role_ids=_excluded_role_ids))

            return roles

        return list(_get_roles(role).keys())

    def _create_token(
        self,
        *,
        validity: timedelta,
        audiences: List[str] = [],
        include_critical: bool = False,
        store_in_db: bool = False,
        token_type: Optional['UserToken.Types'] = None,
    ) -> Tuple[str, str]:
        time_now = timezone.now()
        time_expire = time_now + validity

        token_id = random_string_generator(size=128)

        claims = {
            'iss': settings.JWT_ISSUER,
            'iat': time_now,
            'nbf': time_now,
            'exp': time_expire,
            'sub': self.id,
            'ten': self.tenant.id,
            'crt': include_critical,
            'aud': audiences,
            'rls': [role.name for role in self.get_roles()],
            'jti': token_id,
        }

        token = jwt.encode(
            claims=claims,
            key=settings.JWT_PRIVATE_KEY,
            algorithm='ES512',
        )

        if store_in_db:
            self.tokens.create(id=token_id, type=token_type)

        return token, token_id

    def create_transaction_token(self, include_critical: bool = False, used_token: Optional[Access] = None) -> str:
        audiences: List[str] = [scope.code for scope in self.get_scopes(include_critical=include_critical)]

        if self.status == self.Status.TERMINATED:
            raise AuthError(detail=Error(code='user_terminated'))

        if used_token:
            try:
                user_token = self.tokens.get(id=used_token.token.jti, type=UserToken.Types.USER)

            except UserToken.DoesNotExist as error:
                raise AuthError(detail=Error(code='invalid_user_token')) from error

            if not user_token.is_active:
                raise AuthError(detail=Error(code='invalid_user_token:not_active'))

        token, _ = self._create_token(
            validity=timedelta(minutes=5),
            audiences=audiences,
            include_critical=include_critical,
        )

        return token

    def create_user_token(self) -> str:
        token, token_id = self._create_token(
            validity=timedelta(days=365),
            audiences=[
                'access.users.request_transaction_token'
            ],
            store_in_db=True,
            token_type=UserToken.Types.USER,
        )

        return token

    def _invalidate_old_otps(self, *, type, create_new_threshold: Optional[int] = None):
        old_otps = self.otps.filter(type=type, used_at__isnull=True)
        try:
            scopes = context.access.get().token.get_scopes()
            if AccessScope.from_str('access.users.create_otp.any') in scopes:
                create_new_threshold = None

        except LookupError:
            pass

        for old_otp in old_otps:
            if create_new_threshold and old_otp.created_at > timezone.now() - timedelta(seconds=create_new_threshold):
                raise ConstraintError(detail=Error(code='create_new_otp_threshold_not_reached'))

            old_otp.used_at = timezone.now()
            old_otp.save()

    def request_otp(
        self,
        *,
        type: 'UserOTP.UserOTPType',
        length: Optional[int] = None,
        validity: Optional[int] = None,
        chars: Optional[str] = None,
        create_new_threshold: Optional[int] = None,
        is_internal: bool = False,
    ) -> 'UserOTP':
        if length is None:
            length = getattr(settings, f'AUTH_{type}_LENGTH')

        if validity is None:
            validity = getattr(settings, f'AUTH_{type}_VALIDITY')

        if create_new_threshold is None:
            create_new_threshold = getattr(settings, f'AUTH_{type}_CREATE_NEW_THRESHOLD')

        self._invalidate_old_otps(type=type, create_new_threshold=create_new_threshold)

        kwargs = {}
        if chars:
            kwargs['chars'] = chars

        elif type == UserOTP.UserOTPType.PIN:
            kwargs['chars'] = string.digits

        otp = UserOTP(
            user=self,
            type=type,
            expire_at=timezone.now() + timedelta(seconds=validity),
            is_internal=is_internal,
        )
        otp.set_value(random_string_generator(size=length, **kwargs))
        otp.save()
        return otp

    @atomic
    def save(self, *args, **kwargs):
        modified = self.get_dirty_fields(check_relationship=True)
        if 'email' in modified:
            self.email = self.email.lower()

        if not all([self.first_name, self.last_name]):
            self.first_name = self.last_name = None

        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('tenant', 'email',),
                name='tenant_email_unique',
                condition=(
                    ~models.Q(status='TERMINATED')
                ),
            ),
        ]


class UserToken(models.Model):
    class Types(models.TextChoices):
        USER = 'USER', _('User Token')

    id = models.CharField(max_length=128, primary_key=True, default=_default_user_token_id, editable=False)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    type: str = models.CharField(max_length=16, choices=Types.choices)
    create_date: datetime = models.DateTimeField(auto_now_add=True)
    is_active: bool = models.BooleanField(default=True)


class UserAccessToken(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=_default_user_accesstoken_id, editable=False)
    token: str = models.CharField(max_length=128, unique=True, db_index=True, default=_default_user_accesstoken_token, editable=False)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_tokens')
    last_used: datetime = models.DateTimeField(null=True, blank=True)
    create_date: datetime = models.DateTimeField(auto_now_add=True)
    scopes = models.ManyToManyField(Scope, related_name='user_access_tokens', limit_choices_to={'is_active': True, 'is_internal': False}, blank=True)
    is_active: bool = models.BooleanField(default=True)

    def get_scopes(self, include_critical: bool = True) -> Set[Scope]:
        filters = models.Q()
        if not include_critical:
            filters &= models.Q(is_critical=False)

        return set(self.scopes.filter(filters))

    def create_transaction_token(self, include_critical: bool = False) -> str:
        scopes: Set[Scope] = self.user.get_scopes()
        if self.scopes.count():
            scopes = scopes.intersection(self.get_scopes(include_critical=include_critical))

        audiences: List[str] = [scope.code for scope in scopes]

        token, _ = self.user._create_token(
            validity=timedelta(minutes=5),
            audiences=audiences,
            include_critical=include_critical,
        )

        return token


class UserOTP(KafkaPublishMixin, models.Model):
    _value = None

    class UserOTPType(models.TextChoices):
        PIN = 'PIN', "PIN"
        TOKEN = 'TOKEN', "Token"

    id = models.CharField(max_length=64, primary_key=True, default=_default_user_otp_id)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    type: str = models.CharField(max_length=16, choices=UserOTPType.choices, db_index=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    expire_at: datetime = models.DateTimeField()
    length: int = models.IntegerField()
    used_at: datetime = models.DateTimeField(null=True, blank=True)
    value: str = models.CharField(max_length=128)
    is_internal: bool = models.BooleanField(default=False)

    def set_value(self, value: str):
        self.value = make_password(value)
        self._value = value
        self.length = len(value)

    def validate(self, value):
        return check_password(value, self.value)

    @atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'type', 'used_at',),
                name='user_type_used_at_unique',
            ),
        ]


class UserFlag(models.Model):
    id = models.CharField(max_length=72, primary_key=True, default=_default_user_flag_id)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flags')
    key: str = models.CharField(max_length=64)
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'key',),
                name='user_flag_key_unique',
            ),
        ]
