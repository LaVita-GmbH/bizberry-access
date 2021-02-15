from typing import List, Optional
from pydantic import BaseModel, Field
from olympus.utils.pydantic_django import DjangoORMBaseModel
from ... import models
from . import Role


class User(DjangoORMBaseModel):
    class RoleTenantRel(Role):
        class TenantReference(BaseModel):
            id: str = Field(orm_field=models.UserRoleRelation.tenant)

        id: str = Field(orm_field=models.UserRoleRelation.role)
        tenant: Optional[TenantReference]

        class Config:
            orm_mode = False

    id: str = Field(orm_field=models.User.id)
    email: str = Field(orm_field=models.User.email)
    status: models.User.Status = Field(orm_field=models.User.status)
    roles: List[RoleTenantRel] = Field(orm_field=models.User.roles_rel)
