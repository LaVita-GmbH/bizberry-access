from typing import Optional
from django.utils.translation import TranslatorCommentWarning
from fastapi import APIRouter, Depends, HTTPException, status, Body, Security
from fastapi.security import SecurityScopes
from django.contrib.auth import authenticate as sync_authenticate
from django.conf import settings
from asgiref.sync import sync_to_async
from fautils.wrappers import wrap_into_response
from fautils.schemas import Response
from ..utils import JWTToken
from ..models import User, UserAccessToken
from ..schemas import request, response


router = APIRouter()

user_token = JWTToken(
    scheme_name='User Token',
    auto_error=False,
)

authenticate = sync_to_async(sync_authenticate, thread_sensitive=True)


def get_user(
    scopes: SecurityScopes,
    token: dict = Depends(user_token),
) -> Optional[User]:
    if not token:
        return

    return User.objects.get(id=token['sub'])


@router.post('/user', response_model=Response.wraps(data=response.AuthUser))
@wrap_into_response
async def get_user_token(credentials: request.AuthUser = Body(...)):
    user: User = await authenticate(username=credentials.username, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return response.AuthUser(
        token=response.AuthUserToken(
            refresh=await user.create_user_token(),
        )
    )


@router.post('/transaction', response_model=Response.wraps(data=response.AuthTransaction))
@wrap_into_response
async def get_transaction_token(user: Optional[User] = Security(get_user, scopes=['pegasus.users.request_transaction_token']), credentials: Optional[request.AuthTransaction] = Body(default=None)):
    transaction_token = None

    if credentials and credentials.access_token:
        @sync_to_async
        def get_token_from_access_token(access_token) -> UserAccessToken:
            return UserAccessToken.objects.get(token=access_token)

        user_accesstoken: UserAccessToken = await get_token_from_access_token(credentials.access_token)
        transaction_token = await user_accesstoken.create_transaction_token()

    elif user:
        transaction_token = await user.create_transaction_token()

    else:
        raise HTTPException(status_code=401)

    return response.AuthTransaction(
        token=response.AuthTransactionToken(
            transaction=transaction_token,
        )
    )
