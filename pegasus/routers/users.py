from typing import Dict, Tuple
from fastapi import APIRouter, Security, Body
from fautils.handlers.error import respond_with_error
from fautils.schemas import Response
from fautils.wrappers import wrap_into_response
from ..utils import JWTToken
from ..models import User, Role
from ..schemas import response, request


router = APIRouter()

jwt_token = JWTToken(scheme_name="Transaction Token")


def get_user(token: dict = Security(jwt_token)) -> request.Auth:
    return request.Auth(
        user=User.objects.get(id=token['sub']),
        scopes=tuple(token['aud']),
    )


@router.post('/', response_model=Response.wraps(response.User))
@wrap_into_response
async def create_user(auth: request.Auth = Security(get_user, scopes=['pegasus.users.create']), create_user: request.UserCreate = Body(...)):
    new_user = User.objects.create_user(
        email=create_user.email,
        password=create_user.password,
    )

    for role in create_user.roles:
        new_user.roles.add(Role.objects.get(id=role.id))

    response_user = await response.User.from_orm(new_user)
    return response_user


@router.get('/me', response_model=Response.wraps(response.User))
@wrap_into_response
async def get_me(auth: request.Auth = Security(get_user, scopes=['pegasus.users.read.all', 'pegasus.users.read.me'])):
    response_user = await response.User.from_orm(auth.user)
    return response_user
