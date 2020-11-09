from typing import Optional
from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    username: Optional[str]
    password: str


class AuthTransaction(BaseModel):
    access_token: str
