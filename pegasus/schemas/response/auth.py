from typing import Optional
from pydantic import BaseModel


class AuthUserToken(BaseModel):
    user: str


class AuthUser(BaseModel):
    token: AuthUserToken


class AuthTransactionToken(BaseModel):
    transaction: str


class AuthTransaction(BaseModel):
    token: AuthTransactionToken
