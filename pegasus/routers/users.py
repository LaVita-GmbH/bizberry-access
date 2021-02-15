from typing import Dict, Tuple
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Security, Body
from olympus.exceptions import AccessError
from olympus.schemas import Access
from ..utils import JWTToken
from ..models import User, Role
from ..schemas import response, request


router = APIRouter()

transaction_token = JWTToken(scheme_name="Transaction Token")


def access_user(access: Access = Security(transaction_token)) -> Access:
    access.user = User.objects.get(id=access.user_id)

    return access


@sync_to_async
def get_user_by_id(user_id: str, access: Access):
    user = User.objects.get(id=user_id)
    if access.scope.selector != 'all' and user != access.user:
        raise AccessError

    return user


@sync_to_async
def create_user(body: request.UserCreate):
    new_user = User.objects.create_user(
        email=str(body.email),
        password=str(body.password.get_secret_value()),
    )

    return new_user


@router.post('', response_model=response.User)
async def post_user(access: Access = Security(access_user, scopes=['access.users.create',]), body: request.UserCreate = Body(...)):
    """
    Scopes: `access.users.create`
    """
    new_user = await create_user(body)

    response_user = await response.User.from_orm(new_user)
    return response_user


@router.get('/self', response_model=response.User)
async def get_self(access: Access = Security(access_user, scopes=['access.users.read.own',])):
    """
    Scopes: `access.users.read.own`
    """
    return await get_user(access.user.id, access=access)


@router.get('/{user_id}', response_model=response.User)
async def get_user(user_id: str, access: Access = Security(access_user, scopes=['access.users.read.any', 'access.users.read.own'])):
    """
    Scopes: `access.users.read.any`, `access.users.read.own`
    """
    user = await get_user_by_id(user_id, access)

    return await response.User.from_orm(user)
