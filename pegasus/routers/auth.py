from typing import Optional
from datetime import timedelta
from django.utils import timezone
from fastapi import APIRouter, HTTPException, status, Body, Security
from django.contrib.auth import authenticate as sync_authenticate
from asgiref.sync import sync_to_async
from olympus.schemas import Access, Error
from olympus.exceptions import AuthError
from ..utils import JWTToken
from ..models import User, UserAccessToken
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
def _get_token_from_access_token(access_token, include_critical: bool = False) -> UserAccessToken:
    user_accesstoken: UserAccessToken = UserAccessToken.objects.get(token=access_token)
    return user_accesstoken.create_transaction_token(include_critical=include_critical)


@sync_to_async
def _get_token_for_user(user: User, tenant_id, include_critical: bool = False):
    return user.create_transaction_token(tenant_id, include_critical=include_critical)


@router.post('/user', response_model=response.AuthUser)
async def get_user_token(credentials: request.AuthUser = Body(...)):
    user: User = await authenticate(email=credentials.email, tenant_id=credentials.tenant.id, password=credentials.password)
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

        transaction_token = await _get_token_for_user(access.user, access.tenant_id)

    else:
        raise AuthError

    return response.AuthTransaction(
        token=response.AuthTransactionToken(
            transaction=transaction_token,
        )
    )
