from typing import Callable, List, Tuple
from fastapi import APIRouter, Depends, Security
from fautils.handlers.error import respond_with_error
from fautils.schemas import Response
from fautils.wrappers import wrap_into_response
from ..utils import JWTToken
from ..models import User
from ..schemas import response


router = APIRouter()

jwt_token = JWTToken(scheme_name="Transaction Token")


def get_user(token: dict = Security(jwt_token)) -> User:
    return User.objects.get(id=token['sub'])


@router.post('/', response_model=Response.wraps(response.User))
@wrap_into_response
async def create_user(current_user: User = Security(get_user, scopes=['pegasus.users.create'])):
    raise NotImplementedError


@router.get('/me', response_model=Response.wraps(response.User))
@wrap_into_response
async def get_me(current_user: User = Security(get_user, scopes=['pegasus.users.read.all', 'pegasus.users.read.me'])):
    response_user = await response.User.from_orm(current_user)
    return response_user
