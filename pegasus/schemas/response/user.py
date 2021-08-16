from typing import List, Optional
from datetime import datetime
from olympus.utils.pydantic import Reference, include_reference
from pydantic import BaseModel, Field
from olympus.utils.pydantic_django import DjangoORMBaseModel
from ... import models
from .. import base


@include_reference()
class User(base.User):
    class TenantReference(Reference, rel='olymp/access/tenants'):
        id: str = Field(orm_field=models.User.tenant)

    id: str = Field(orm_field=models.User.id)
    tenant: TenantReference
    email: str = Field(orm_field=models.User.email)
    status: models.User.Status = Field(orm_field=models.User.status)
    created_at: datetime = Field(orm_field=models.User.date_joined)
    is_password_usable: bool = Field(orm_method=models.User.has_usable_password)


class UsersList(BaseModel):
    users: List[User]


class UserAccessToken(DjangoORMBaseModel):
    token: str = Field(orm_field=models.UserAccessToken.token)
