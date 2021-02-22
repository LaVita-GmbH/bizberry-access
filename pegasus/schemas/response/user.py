from typing import Optional
from pydantic import BaseModel, Field
from olympus.utils.pydantic_django import DjangoORMBaseModel
from ... import models


class User(DjangoORMBaseModel):
    class TenantReference(BaseModel):
        id: str = Field(orm_field=models.User.tenant)

    class RoleReference(BaseModel):
        id: str = Field(orm_field=models.User.role)

    id: str = Field(orm_field=models.User.id)
    tenant: TenantReference
    email: str = Field(orm_field=models.User.email)
    status: models.User.Status = Field(orm_field=models.User.status)
    role: Optional[RoleReference]
