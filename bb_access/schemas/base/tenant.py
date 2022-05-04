from typing import Optional
from pydantic import Field
from djfapi.utils.pydantic_django import DjangoORMBaseModel
from ... import models


class Tenant(DjangoORMBaseModel):
    name: Optional[str] = Field(orm_field=models.Tenant.name)


class TenantCountry(DjangoORMBaseModel):
    code: str = Field(description="ISO 3166 Alpha-2 Country Code", orm_field=models.TenantCountry.code)