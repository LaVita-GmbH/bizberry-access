from typing import Optional
from pydantic import BaseModel, Field
from ...models import User
from . import TenantReference


class AuthUser(BaseModel):
    email: Optional[str]
    password: str
    tenant: TenantReference


class AuthTransaction(BaseModel):
    access_token: str
