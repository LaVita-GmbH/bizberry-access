from pydantic import Field
from olympus.utils import DjangoORMBaseModel
from ... import models


class Role(DjangoORMBaseModel):
    name: str = Field(max_length=56, orm_field=models.Role.name)
    is_default: bool = Field(orm_field=models.Role.is_default)
    is_active: bool = Field(orm_field=models.Role.is_active)
