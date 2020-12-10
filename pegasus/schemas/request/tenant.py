from typing import Optional
from pydantic import BaseModel


class TenantReference(BaseModel):
    id: str


class TenantUpdate(BaseModel):
    name: Optional[str]


class TenantCountryCreate(BaseModel):
    code: str
