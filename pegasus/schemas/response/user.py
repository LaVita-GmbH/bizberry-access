from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ... import models
from .. import base


class User(base.User):
    class TenantReference(BaseModel):
        id: str = Field(orm_field=models.User.tenant)

    class RoleReference(BaseModel):
        id: str = Field(orm_field=models.User.role)

    id: str = Field(orm_field=models.User.id)
    tenant: TenantReference
    email: str = Field(orm_field=models.User.email)
    status: models.User.Status = Field(orm_field=models.User.status)
    role: Optional[RoleReference]
    created_at: datetime = Field(orm_field=models.User.date_joined)


class UsersList(BaseModel):
    users: List[User]
