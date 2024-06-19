from typing import Optional

from pydantic import BaseModel

from bb_access.schemas import base


class TenantReference(BaseModel):
    id: str


class TenantUpdate(base.Tenant):
    pass


class TenantCountryCreate(BaseModel):
    code: str
