from typing import Optional
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Body, Security, Path
from django.db.transaction import atomic
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate as sync_authenticate
from django.contrib.auth.signals import user_logged_in
from validate_email import validate_email
from djdantic.schemas import Access, Error
from djfapi.exceptions import AuthError, ValidationError

from bb_access.utils import JWTToken
from bb_access.models import User, UserAccessToken, UserOTP
from bb_access.schemas import request, response


router = APIRouter()

user_token = JWTToken(
    scheme_name="User Token",
    auto_error=False,
)
transaction_token = JWTToken(scheme_name="Transaction Token")


def authenticate(*args, **kwargs) -> Optional[User]:
    user = sync_authenticate(*args, **kwargs)
    if user:
        user_logged_in.send(
            sender=user.__class__, instance=user, user=user, request=None
        )

    return user


def access_user(access: Optional[Access] = Security(user_token)) -> Access:
    if not access:
        return

    access.user = User.objects.get(id=access.user_id)

    return access


@atomic
def _reset_password(
    tenant_id: str,
    *,
    user: Optional[User] = None,
    otp_id: Optional[str] = None,
    value: str,
    password: str
) -> Optional[User]:
    if not user and not otp_id:
        raise ValidationError(detail=Error(code="user_or_id_required"))

    otp: UserOTP
    if otp_id:
        otp = UserOTP.objects.get(
            id=otp_id,
            user__tenant_id=tenant_id,
            used_at__isnull=True,
            type=UserOTP.UserOTPType.TOKEN,
        )
        user = otp.user

    elif user:
        otp = user.otps.get(used_at__isnull=True, type=UserOTP.UserOTPType.TOKEN)

    else:
        raise NotImplementedError

    if not otp.validate(value):
        return None

    otp.used_at = timezone.now()
    otp.save(
        update_fields=[
            "used_at",
        ]
    )
    user.set_password(password)
    user.save()
    user_logged_in.send(sender=user.__class__, instance=user, user=user, request=None)

    return user


@router.post("/user", response_model=response.AuthUser)
def get_user_token(credentials: request.AuthUser = Body(...)):
    _user = None
    if credentials.otp:
        user: User = _reset_password(
            tenant_id=credentials.tenant.id,
            otp_id=credentials.otp.id,
            value=credentials.otp.value,
            password=credentials.password,
        )

    elif credentials.email or credentials.id:
        if credentials.email:
            try:
                _user: User = User.objects.get(
                    status=User.Status.ACTIVE,
                    tenant_id=credentials.tenant.id,
                    email=credentials.email.lower(),
                )

            except User.DoesNotExist:
                _user: User = User.objects.get(
                    status=User.Status.ACTIVE,
                    tenant_id=credentials.tenant.id,
                    number=credentials.email,
                )

        elif credentials.id:
            _user: User = User.objects.get(
                status=User.Status.ACTIVE,
                tenant_id=credentials.tenant.id,
                id=credentials.id,
            )

        else:
            raise NotImplementedError

        user: User = authenticate(id=_user.id, password=credentials.password)

    else:
        raise NotImplementedError

    if not user:
        if _user and not _user.has_usable_password():
            raise AuthError(detail=Error(code="password_reset_required"))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = user.create_user_token()

    return response.AuthUser(
        token=response.AuthUserToken(
            user=token,
        ),
        via=getattr(user, "_login_via", User.LoginMethod.PASSWORD),
    )


@router.post("/transaction", response_model=response.AuthTransaction)
def get_transaction_token(
    access: Optional[Access] = Security(
        access_user, scopes=["access.users.request_transaction_token"]
    ),
    credentials: Optional[request.AuthTransaction] = Body(default=None),
):
    """
    Scopes: `access.users.request_transaction_token`
    """
    transaction_token = None
    include_critical = credentials and credentials.include_critical or False

    if credentials and credentials.access_token:
        user_accesstoken: UserAccessToken = UserAccessToken.objects.get(
            token=credentials.access_token, is_active=True
        )
        transaction_token = user_accesstoken.create_transaction_token(
            include_critical=include_critical
        )

    elif access and access.user:
        if include_critical and access.token.iat < timezone.now() - timedelta(
            seconds=settings.AUTH_TOKEN_CRITICAL_THRESHOLD
        ):
            raise AuthError(
                detail=Error(
                    type="AuthError",
                    code="token_too_old_for_include_critical",
                )
            )

        transaction_token = access.user.create_transaction_token(
            include_critical=include_critical, used_token=access
        )

    else:
        raise AuthError

    return response.AuthTransaction(
        token=response.AuthTransactionToken(
            transaction=transaction_token,
        )
    )


@router.post("/otp", response_model=response.AuthOTP)
def post_otp(
    body: request.AuthUserReset = Body(...),
):
    """
    Request a one time password (used as PIN or TOKEN)
    """
    user: User = User.objects.get(
        status=User.Status.ACTIVE, email=body.email.lower(), tenant_id=body.tenant.id
    )
    otp: UserOTP = user.request_otp(type=body.type)
    return response.AuthOTP.from_orm(otp)
