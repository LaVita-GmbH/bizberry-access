from typing import Dict, Tuple
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Security, Body
from olympus.exceptions import AccessError
from ..utils import JWTToken
from ..models import User, Role
from ..schemas import response, request


router = APIRouter()

jwt_token = JWTToken(scheme_name="Transaction Token")


def auth_user(token: dict = Security(jwt_token)) -> request.Auth:
    return request.Auth(
        user=User.objects.get(id=token['sub']),
        scope=token['scope'],
    )


@sync_to_async
def get_user_by_id(user_id: str, auth: request.Auth):
    user = User.objects.get(id=user_id)
    if auth.scope.selector != 'all' and user != auth.user:
        raise AccessError

    return user


@sync_to_async
def create_user(body: request.UserCreate):
    new_user = User.objects.create_user(
        email=str(body.email),
        password=str(body.password),
    )

    for role in body.roles:
        new_user.roles.add(Role.objects.get(id=role.id))

    return new_user


@router.post('/', response_model=response.User)
async def post_user(auth: request.Auth = Security(auth_user, scopes=['pegasus.users.create',]), body: request.UserCreate = Body(...)):
    new_user = await create_user(body)

    response_user = await response.User.from_orm(new_user)
    return response_user


@router.get('/me', response_model=response.User)
async def get_me(auth: request.Auth = Security(auth_user, scopes=['pegasus.users.read.me',])):
    return await get_user(auth.user.id, auth=auth)


@router.get('/{user_id}', response_model=response.User)
async def get_user(user_id: str, auth: request.Auth = Security(auth_user, scopes=['pegasus.users.read.all', 'pegasus.users.read.me'])):
    user = await get_user_by_id(user_id, auth)

    return await response.User.from_orm(user)
