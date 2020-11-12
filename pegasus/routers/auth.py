from typing import Optional
from django.utils.translation import TranslatorCommentWarning
from fastapi import APIRouter, Depends, HTTPException, status, Body, Security
from fastapi.security import SecurityScopes
from django.contrib.auth import authenticate as sync_authenticate
from django.conf import settings
from asgiref.sync import sync_to_async
from olympus.schemas import Access
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


@router.post('/user', response_model=response.AuthUser)
async def get_user_token(credentials: request.AuthUser = Body(...)):
    user: User = await authenticate(email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return response.AuthUser(
        token=response.AuthUserToken(
            user=await user.create_user_token(tenant=credentials.tenant.id),
        )
    )


@router.post('/transaction', response_model=response.AuthTransaction)
async def get_transaction_token(access: Optional[Access] = Security(access_user, scopes=['pegasus.users.request_transaction_token']), credentials: Optional[request.AuthTransaction] = Body(default=None)):
    transaction_token = None

    if credentials and credentials.access_token:
        @sync_to_async
        def get_token_from_access_token(access_token) -> UserAccessToken:
            return UserAccessToken.objects.get(token=access_token)

        user_accesstoken: UserAccessToken = await get_token_from_access_token(credentials.access_token)
        transaction_token = await user_accesstoken.create_transaction_token()

    elif access and access.user:
        transaction_token = await access.user.create_transaction_token(access.tenant_id)

    else:
        raise AuthError

    return response.AuthTransaction(
        token=response.AuthTransactionToken(
            transaction=transaction_token,
        )
    )
