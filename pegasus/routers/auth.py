from typing import Optional
from datetime import timedelta
from django.db.transaction import atomic
from django.utils import timezone
from fastapi import APIRouter, HTTPException, status, Body, Security, Path
from django.contrib.auth import authenticate as sync_authenticate
from olympus.utils.sync import sync_to_async
from olympus.schemas import Access, Error
from olympus.exceptions import AccessError, AuthError, ValidationError
from ..utils import JWTToken
from ..models import User, UserAccessToken, UserOTP
from ..schemas import request, response


router = APIRouter()

user_token = JWTToken(
    scheme_name='User Token',
    auto_error=False,
)

authenticate = sync_to_async(sync_authenticate, thread_sensitive=True)


def access_user(access: Optional[Access] = Security(user_token)) -> Access:
    if not access:
        return

    access.user = User.objects.get(id=access.user_id)

    return access


@sync_to_async
def _create_token(user):
    return user.create_user_token()


@sync_to_async
def _get_token_from_access_token(access_token, include_critical: bool = False) -> str:
    user_accesstoken: UserAccessToken = UserAccessToken.objects.get(token=access_token, is_active=True)
    return user_accesstoken.create_transaction_token(include_critical=include_critical)


@sync_to_async
def _get_token_for_user(access: Access, user: User, include_critical: bool = False) -> str:
    return user.create_transaction_token(include_critical=include_critical, used_token=access)


@sync_to_async
def _get_user(**filters):
    return User.objects.get(**filters)


@sync_to_async
@atomic
def _reset_password(tenant_id: str, *, user: Optional[User] = None, otp_id: Optional[str] = None, value: str, password: str) -> Optional[User]:
    if not user and not otp_id:
        raise ValidationError(detail=Error(code='user_or_id_required'))

    otp: UserOTP
    if otp_id:
        otp = UserOTP.objects.get(id=otp_id, user__tenant_id=tenant_id, used_at__isnull=True, type=UserOTP.UserOTPType.TOKEN)
        user = otp.user

    elif user:
        otp = user.otps.get(used_at__isnull=True, type=UserOTP.UserOTPType.TOKEN)

    else:
        raise NotImplementedError

    if not otp.validate(value):
        return None

    otp.used_at = timezone.now()
    otp.save(update_fields=['used_at',])
    user.set_password(password)
    return user


@router.post('/user', response_model=response.AuthUser)
async def get_user_token(credentials: request.AuthUser = Body(...)):
    if credentials.otp:
        user: User = await _reset_password(
            tenant_id=credentials.tenant.id,
            otp_id=credentials.otp.id,
            value=credentials.otp.value,
            password=credentials.password,
        )

    elif credentials.email:
        user = await _get_user(email=credentials.email, tenant_id=credentials.tenant.id)
        user: User = await authenticate(id=user.id, password=credentials.password)

    else:
        raise NotImplementedError

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = await _create_token(user)

    return response.AuthUser(
        token=response.AuthUserToken(
            user=token,
        )
    )


@router.post('/transaction', response_model=response.AuthTransaction)
async def get_transaction_token(
    access: Optional[Access] = Security(access_user, scopes=['access.users.request_transaction_token']),
    credentials: Optional[request.AuthTransaction] = Body(default=None),
):
    """
    Scopes: `access.users.request_transaction_token`
    """
    transaction_token = None
    include_critical = credentials and credentials.include_critical or False

    if credentials and credentials.access_token:
        transaction_token = await _get_token_from_access_token(credentials.access_token, include_critical=include_critical)

    elif access and access.user:
        if include_critical and access.token.iat < timezone.now() - timedelta(hours=1):
            raise AuthError(detail=Error(
                type='AuthError',
                code='token_too_old_for_include_critical',
            ))

        transaction_token = await _get_token_for_user(access, access.user, include_critical=include_critical)

    else:
        raise AuthError

    return response.AuthTransaction(
        token=response.AuthTransactionToken(
            transaction=transaction_token,
        )
    )


@router.post('/otp', response_model=response.AuthOTP)
async def post_otp(
    body: request.AuthUserReset = Body(...),
):
    """
    Request a one time password (used as PIN or TOKEN)
    """
    user: User = await _get_user(email=body.email, tenant_id=body.tenant.id)
    otp: UserOTP = await sync_to_async(user.request_otp)(type=body.type)
    return await response.AuthOTP.from_orm(otp)
