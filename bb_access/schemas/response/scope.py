from pydantic import Field

from bb_access import models
from bb_access.schemas import base


class Scope(base.Scope):
    id: str = Field(min_length=32, max_length=32, orm_field=models.Scope.id)
