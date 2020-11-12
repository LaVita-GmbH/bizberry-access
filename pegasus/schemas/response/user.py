from enum import Enum
from typing import List, Set
from pydantic import BaseModel, Field
from ... import models
from . import Role


class User(BaseModel):
    class Status(str, Enum):
        ACTIVE = 'active'
        TERMINATED = 'terminated'

    id: str
    email: str
    status: Status
    roles: List[Role]

    class Config:
        orm_mode = True

    @classmethod
    async def from_orm(cls, obj: models.User, tenant: str):
        values = {
            'id': obj.id,
            'email': obj.email,
            'status': obj.status,
            'roles': [Role.from_orm(role) for role in await obj.get_roles(tenant=tenant)],
        }
        return cls(**values)
