from fastapi import APIRouter
from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer


router = APIRouter()


@router.get('/me')
def get_me():
    raise NotImplementedError
