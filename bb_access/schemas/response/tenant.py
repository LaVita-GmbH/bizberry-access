from typing import List, Optional

from pydantic import BaseModel, Field

from bb_access import models
from bb_access.schemas import base


class TenantCountry(base.TenantCountry):
    id: str = Field(orm_field=models.TenantCountry.id)


class TenantCountriesList(BaseModel):
    countries: List[TenantCountry]


class Tenant(base.Tenant):
    id: str = Field(min_length=16, max_length=16, orm_field=models.Tenant.id)
    countries: List[TenantCountry] = Field(orm_field=models.Tenant.countries)

    class Config:
        arbitrary_types_allowed = True


class TenantsList(BaseModel):
    tenants: List[Tenant]
