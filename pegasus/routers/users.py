from typing import Callable, List, Tuple
from fastapi import APIRouter, Depends, Security
from fautils.security.jwt import get_token
from ..utils import JWTToken
from ..models import User


router = APIRouter()

jwt_token = JWTToken(scheme_name="Transaction Token")


def get_user(token: dict = Security(jwt_token)) -> User:
    return User.objects.get(id=token['sub'])


@router.get('/me')
def get_me(user: User = Security(get_user, scopes=['pegasus.users.read.all', 'pegasus.users.read.me'])):
    raise NotImplementedError
