from typing import Optional
from pydantic import BaseModel, Field
from ...models import User
from . import TenantReference


class AuthUser(BaseModel):
    email: Optional[str]
    password: str
    tenant: TenantReference


class AuthTransaction(BaseModel):
    include_critical: bool = Field(False, description="Include critical scopes in the token. To obtain a transaction token with critical scopes using an user token, the token may not be issued more than 1 hour in the past.")
    access_token: Optional[str] = None
