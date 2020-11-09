from fastapi import APIRouter, Depends, HTTPException, status, Body
from django.contrib.auth import authenticate as sync_authenticate
from django.conf import settings
from asgiref.sync import sync_to_async
from fautils.wrappers import wrap_into_response
from fautils.schemas import Response
from fautils.security.jwt import JWTToken
from ..models import User
from ..schemas import request, response


router = APIRouter()

user_token = JWTToken(
    name="Authorization",
    key=settings.JWT_PUBLIC_KEY,
    algorithm='ES512',
    audiences=['pegasus.users.request_transaction_token'],
)

authenticate = sync_to_async(sync_authenticate, thread_sensitive=True)


def get_user(
    token: dict = Depends(user_token),
) -> User:
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
async def get_transaction_token(user: User = Depends(get_user)):
    return response.AuthTransaction(
        token=response.AuthTransactionToken(
            transaction=await user.create_transaction_token()
        )
    )
