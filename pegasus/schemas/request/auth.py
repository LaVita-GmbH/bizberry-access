from typing import Optional
from pydantic import BaseModel, Field
from olympus.security.jwt import Scope
from ...models import User


class Auth(BaseModel):
    user: User
    scope: Scope

    class Config:
        arbitrary_types_allowed = True


class AuthUser(BaseModel):
    username: Optional[str]
    password: str


class AuthTransaction(BaseModel):
    access_token: str
