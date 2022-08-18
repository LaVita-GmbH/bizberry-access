from djdantic import Field, BaseModel
from ... import models


class Role(BaseModel, orm_model=models.Role):
    name: str = Field(max_length=56, orm_field=models.Role.name)
    is_default: bool = Field(orm_field=models.Role.is_default)
    is_active: bool = Field(orm_field=models.Role.is_active)
