from typing import List

from pydantic import BaseModel, Field
from djdantic.utils.pydantic_django import DjangoORMBaseModel
from djdantic.utils.pydantic import Reference, include_reference

from bb_access import models
from bb_access.schemas import base
from .scope import Scope


@include_reference()
class Role(base.Role):
    @include_reference()
    class RoleReference(DjangoORMBaseModel, Reference, rel="bizberry/access/roles"):
        id: str = Field(min_length=32, max_length=32, orm_field=models.Role.id)

    id: str = Field(min_length=32, max_length=32, orm_field=models.Role.id)
    scopes: List[Scope] = Field(orm_method=models.Role.get_scopes)
    included_roles: List[RoleReference] = Field(
        orm_method=models.Role.get_included_roles
    )


class RolesList(BaseModel):
    roles: List[Role]
