from typing import Optional
from pydantic import Field
from olympus.utils import DjangoORMBaseModel
from ... import models


class Scope(DjangoORMBaseModel):
    service: str = Field(max_length=32, orm_field=models.Scope.service)
    resource: str = Field(max_length=24, orm_field=models.Scope.resource)
    action: str = Field(max_length=24, orm_field=models.Scope.action)
    selector: Optional[str] = Field(max_length=48, orm_field=models.Scope.selector)
    is_active: bool = Field(orm_field=models.Scope.is_active)
    is_internal: bool = Field(orm_field=models.Scope.is_internal)
    is_critical: bool = Field(orm_field=models.Scope.is_critical)
