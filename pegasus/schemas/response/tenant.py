from typing import List, Optional
from pydantic import BaseModel, Field
from ...models import Tenant, TenantCountry


class TenantCountry(BaseModel):
    id: str
    code: str = Field(description="ISO 3166 Alpha-2 Country Code")

    class Config:
        orm_mode = True

    @classmethod
    async def from_orm(cls, obj: TenantCountry):
        return cls(
            id=obj.id,
            code=obj.code,
        )


class TenantCountriesList(BaseModel):
    countries: List[TenantCountry]


class Tenant(BaseModel):
    id: str
    name: Optional[str] = None
    countries: List[TenantCountry]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

    @classmethod
    async def from_orm(cls, obj: Tenant):
        countries = await obj.get_countries()

        return cls(
            id=obj.id,
            name=obj.name,
            countries=[await TenantCountry.from_orm(country) for country in countries],
        )


class TenantsList(BaseModel):
    tenants: List[Tenant]
