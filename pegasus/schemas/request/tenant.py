from typing import Optional
from pydantic import BaseModel


class TenantReference(BaseModel):
    id: str


class TenantPatch(BaseModel):
    name: Optional[str]


class TenantCountryCreate(BaseModel):
    code: str
