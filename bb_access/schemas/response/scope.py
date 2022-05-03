from pydantic import Field
from ... import models
from .. import base


class Scope(base.Scope):
    id: str = Field(min_length=32, max_length=32, orm_field=models.Scope.id)
