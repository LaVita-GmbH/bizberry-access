from typing import Optional
from djdantic import Field, BaseModel
from ... import models


class Tenant(BaseModel, orm_model=models.Tenant):
    name: Optional[str] = Field(orm_field=models.Tenant.name)


class TenantCountry(BaseModel, orm_model=models.TenantCountry):
    code: str = Field(description="ISO 3166 Alpha-2 Country Code", orm_field=models.TenantCountry.code)
